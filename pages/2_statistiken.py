import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from supabase import create_client
import urllib.parse

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()
response = supabase.table("dart_averages").select("*").order("play_date").execute()

if not response.data:
    st.info("Noch keine Daten vorhanden.")
    st.stop()

df = pd.DataFrame(response.data)
df['play_date'] = pd.to_datetime(df['play_date'])

# --- DATUMSFILTER ---
min_date = df['play_date'].min().date()
max_date = df['play_date'].max().date()

st.write("### 📅 Analyse-Zeitraum")
st.markdown("<div style='color: #888; font-size: 0.85rem; margin-bottom: 10px;'>Wähle hier den Zeitraum für alle folgenden Metriken und Diagramme.</div>", unsafe_allow_html=True)
date_selection = st.date_input("Auswahl", value=(min_date, max_date), min_value=min_date, max_value=max_date, format="DD.MM.YYYY", label_visibility="collapsed")

if len(date_selection) == 2:
    mask = (df['play_date'].dt.date >= date_selection[0]) & (df['play_date'].dt.date <= date_selection[1])
    df_filtered = df.loc[mask].copy()
else:
    df_filtered = df.copy()

if df_filtered.empty:
    st.warning("Keine Daten im ausgewählten Zeitraum.")
    st.stop()

apple_colors = {"Hanno": "#007AFF", "Dominik": "#FF9500"}
st.divider()

# --- KPIs ---
st.write("### 🏆 Performance-Metriken")
# Symbole im Tab durch angepasste Buchstaben ersetzt
tab1, tab2 = st.tabs(["🔵 H", "🟠 D"])

for tab, player in zip([tab1, tab2], ["Hanno", "Dominik"]):
    with tab:
        player_df = df_filtered[df_filtered['player'] == player].copy()
        if not player_df.empty:
            avg_mean = player_df['average'].mean()
            avg_median = player_df['average'].median()
            max_avg = player_df['average'].max()
            min_avg = player_df['average'].min()
            
            form_avg = player_df['average'].tail(5).mean() if len(player_df) >= 5 else avg_mean
            
            avatar_class, letter = ("avatar-h", "H") if player == "Hanno" else ("avatar-d", "D")
            st.markdown(f"<div style='display:flex; justify-content:center;'><div class='avatar {avatar_class}'>{letter}</div></div>", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            c1.metric("Ø Gesamtschnitt", f"{avg_mean:.2f}")
            c2.metric("Typischer Schnitt (Median)", f"{avg_median:.2f}")
            
            c3, c4 = st.columns(2)
            c3.metric("Aktuelle Form (Letzte 5)", f"{form_avg:.2f}", delta=f"{(form_avg - avg_mean):.2f}", delta_color="normal")
            c4.metric("Höchster Schnitt", f"{max_avg:.2f}", help=f"Schwächstes Spiel in diesem Zeitraum: {min_avg:.2f}")
        else:
            st.info("Keine Daten.")

st.divider()

# --- HEAD TO HEAD ---
st.write("### ⚔️ Head-to-Head & Streaks")
st.markdown("<div style='color: #888; font-size: 0.85rem; margin-bottom: 15px;'>Wer performt an gemeinsamen Spieltagen besser? Zählt als ein Sieg pro Tag.</div>", unsafe_allow_html=True)
daily_avg = df_filtered.groupby(['play_date', 'player'])['average'].mean().unstack()

if 'Hanno' in daily_avg.columns and 'Dominik' in daily_avg.columns:
    h2h_df = daily_avg.dropna(subset=['Hanno', 'Dominik']).sort_index()
    if not h2h_df.empty:
        h2h_df['winner'] = np.select([h2h_df['Hanno'] > h2h_df['Dominik'], h2h_df['Dominik'] > h2h_df['Hanno']], ['Hanno', 'Dominik'], default='Draw')
        h1, h2, h3 = st.columns(3)
        h1.metric("Siege Hanno", (h2h_df['winner'] == 'Hanno').sum())
        h2.metric("Draws", (h2h_df['winner'] == 'Draw').sum())
        h3.metric("Siege Dominik", (h2h_df['winner'] == 'Dominik').sum())
    else:
        st.info("Keine gemeinsamen Spieltage.")

st.divider()

# --- ROLLING AVERAGE (GEFILTERT AUF ZEITRAUM) ---
st.write("### 🌊 Form-Kurve (Trend)")
st.markdown("<div style='color: #888; font-size: 0.85rem; margin-bottom: 15px;'>Der gleitende Durchschnitt (10 Lags) bezogen auf die Spiele im gewählten Zeitraum.</div>", unsafe_allow_html=True)

# Berechnung auf den gefilterten Daten
df_ma_filtered = df_filtered.sort_values(by=['play_date', 'id']).copy()
df_ma_filtered['spiel_total_nr'] = df_ma_filtered.groupby('player').cumcount() + 1
df_ma_filtered['Rolling'] = df_ma_filtered.groupby('player')['average'].transform(lambda x: x.rolling(window=10, min_periods=1).mean())

fig_ma = px.line(df_ma_filtered, x='play_date', y='Rolling', color='player', color_discrete_map=apple_colors, markers=True)
fig_ma.update_traces(line=dict(width=4))
fig_ma.update_layout(legend=dict(orientation="h", y=1.02), margin=dict(l=0, r=0, t=30, b=0))
fig_ma.update_xaxes(title="Datum", showgrid=False)
fig_ma.update_yaxes(title="Ø 10 Spiele", showgrid=True)
st.plotly_chart(fig_ma, use_container_width=True)

st.divider()

# --- BOGEY NUMBER HISTOGRAMM ---
st.write("### 🧱 Barriere-Analyse (Verteilung)")
st.markdown("<div style='color: #888; font-size: 0.85rem; margin-bottom: 15px;'>Wie oft werft ihr welchen Schnitt? Zeigt eure typischen Cluster.</div>", unsafe_allow_html=True)
fig_hist = px.histogram(df_filtered, x='average', color='player', barmode='group', nbins=15, color_discrete_map=apple_colors)
fig_hist.update_layout(legend=dict(orientation="h", y=1.02), margin=dict(l=0, r=0, t=30, b=0))
fig_hist.update_xaxes(title="3er Schnitt Spanne", showgrid=False)
fig_hist.update_yaxes(title="Anzahl der Spiele", showgrid=True)
st.plotly_chart(fig_hist, use_container_width=True)

st.divider()

# --- TAGESVERLAUF MIT ZAHLEN ---
st.write("### ⏱️ Warm-up vs. Ermüdung")
st.markdown("<div style='color: #888; font-size: 0.85rem; margin-bottom: 15px;'>Wie entwickelt sich euer Schnitt vom ersten Lag des Tages bis zum letzten?</div>", unsafe_allow_html=True)

df_intraday = df_filtered.sort_values(by=['play_date', 'id']).copy()
df_intraday['spiel_nr'] = df_intraday.groupby(['play_date', 'player']).cumcount() + 1
df_intra_grouped = df_intraday.groupby(['spiel_nr', 'player'], as_index=False)['average'].mean()

fig_intra = px.line(df_intra_grouped, x='spiel_nr', y='average', color='player', markers=True, color_discrete_map=apple_colors)
fig_intra.update_traces(line=dict(width=3))
fig_intra.update_layout(legend=dict(orientation="h", y=1.02), margin=dict(l=0, r=0, t=30, b=0), xaxis=dict(tickmode='linear', dtick=1))
fig_intra.update_xaxes(title="Lag des Tages", showgrid=False)
fig_intra.update_yaxes(title="Ø Schnitt", showgrid=True)
st.plotly_chart(fig_intra, use_container_width=True)

st.markdown("<div style='color: #888; font-size: 0.85rem; margin-bottom: 10px;'>Ø Schnitt in Zahlen je Lag-Nummer:</div>", unsafe_allow_html=True)
df_intra_pivot = df_intra_grouped.pivot(index='spiel_nr', columns='player', values='average').round(1)
df_intra_pivot.index.name = 'Lag Nr.'
st.dataframe(df_intra_pivot, use_container_width=True)

st.divider()

# --- TABELLE & EXPORT ---
st.write("### 📋 Alle Spiele im Zeitraum & Export")

if 'comment' not in df_filtered.columns: df_filtered['comment'] = ""
df_table = df_filtered.sort_values(by=['play_date', 'id'], ascending=[False, False])
df_table['Datum'] = df_table['play_date'].dt.strftime('%d.%m.%Y')
df_table['Kommentar'] = df_table['comment'].fillna("")

st.dataframe(df_table[["Datum", "player", "average", "Kommentar"]].rename(columns={"player": "Spieler", "average": "Schnitt"}), 
             use_container_width=True, hide_index=True)

col_exp1, col_exp2 = st.columns(2)

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False, sep=";").encode('utf-8-sig')

csv_data = convert_df(df_table[["Datum", "player", "average", "Kommentar"]].rename(columns={"player": "Spieler", "average": "Schnitt"}))
file_name = f"Darts_Export_{date_selection[0].strftime('%Y%m%d')}_bis_{date_selection[1].strftime('%Y%m%d')}.csv"

with col_exp1:
    st.download_button("📥 Als CSV exportieren", data=csv_data, file_name=file_name, mime="text/csv", use_container_width=True)

with col_exp2:
    if not df_filtered.empty:
        h_avg = df_filtered[df_filtered['player'] == 'Hanno']['average'].mean()
        d_avg = df_filtered[df_filtered['player'] == 'Dominik']['average'].mean()
        
        h_text = f"{h_avg:.2f}" if pd.notna(h_avg) else "-"
        d_text = f"{d_avg:.2f}" if pd.notna(d_avg) else "-"
        
        subject = f"🎯 Darts Update ({date_selection[0].strftime('%d.%m.')} - {date_selection[1].strftime('%d.%m.')})"
        body = f"Hier sind unsere neuesten Dart-Statistiken!\n\nØ Hanno: {h_text}\nØ Dominik: {d_text}\n\nGespielte Lags in diesem Zeitraum: {len(df_filtered)}\n\nGesendet aus dem Road to 180 Tracker."
        mailto_link = f"mailto:?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
        st.link_button("📧 Zusammenfassung per Mail", mailto_link, use_container_width=True)
    else:
        st.button("📧 Zusammenfassung per Mail", disabled=True, use_container_width=True)
