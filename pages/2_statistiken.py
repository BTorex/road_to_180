import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# Daten abrufen (inkl. 'id' für die chronologische Sortierung der Lags später)
response = supabase.table("dart_averages").select("*").order("play_date").execute()

if not response.data:
    st.info("Noch keine Daten vorhanden. Tragt zuerst ein paar Averages ein!")
    st.stop()

df = pd.DataFrame(response.data)
df['play_date'] = pd.to_datetime(df['play_date'])

# --- DATUMSFILTER ---
min_date = df['play_date'].min().date()
max_date = df['play_date'].max().date()

st.write("### 📅 Zeitraum")
date_selection = st.date_input(
    "Auswahl",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    format="DD.MM.YYYY",
    label_visibility="collapsed"
)

if len(date_selection) == 2:
    start_date, end_date = date_selection
    mask = (df['play_date'].dt.date >= start_date) & (df['play_date'].dt.date <= end_date)
    df_filtered = df.loc[mask].copy()
else:
    df_filtered = df.copy()

if df_filtered.empty:
    st.warning("Keine Daten im ausgewählten Zeitraum.")
    st.stop()

st.divider()

# --- UMFANGREICHE KPIs ---
st.write("### 🏆 Performance-Analyse")
tab1, tab2 = st.tabs(["🎯 Hanno", "🎯 Dominik"])

for tab, player in zip([tab1, tab2], ["Hanno", "Dominik"]):
    with tab:
        avatar_class = "avatar-h" if player == "Hanno" else "avatar-d"
        letter = "H" if player == "Hanno" else "D"
        st.markdown(f"<div class='avatar-container'><div class='avatar {avatar_class}'>{letter}</div></div>", unsafe_allow_html=True)
        player_df = df_filtered[df_filtered['player'] == player].copy()
        
        if not player_df.empty:
            avg_mean = player_df['average'].mean()
            avg_median = player_df['average'].median()
            max_avg = player_df['average'].max()
            min_avg = player_df['average'].min()
            games_played = len(player_df)
            
            # A-Game (Top 10% Schnitt)
            top_10_percent_count = max(1, int(games_played * 0.10))
            a_game_avg = player_df.nlargest(top_10_percent_count, 'average')['average'].mean()
            
            # Form-Trend
            if games_played >= 5:
                form_avg = player_df['average'].tail(5).mean()
                form_delta = form_avg - avg_mean
            else:
                form_avg = avg_mean
                form_delta = 0.0

            st.caption(f"Basierend auf {games_played} registrierten Sessions.")
            
            c1, c2 = st.columns(2)
            c1.metric("Ø Gesamtschnitt", f"{avg_mean:.2f}")
            c2.metric("Typischer Schnitt (Median)", f"{avg_median:.2f}", help="Robuster gegen Ausreißer als der Durchschnitt.")
            
            c3, c4 = st.columns(2)
            c3.metric("Aktuelle Form (Letzte 5)", f"{form_avg:.2f}", delta=f"{form_delta:.2f} zum Ø", delta_color="normal")
            c4.metric("A-Game (Top 10%)", f"{a_game_avg:.2f}", help="Dein Durchschnitt, wenn es richtig gut läuft.")
            
            c5, c6 = st.columns(2)
            c5.metric("Höchster Schnitt", f"{max_avg:.2f}")
            c6.metric("Schwächstes Spiel", f"{min_avg:.2f}")
            
        else:
            st.info(f"Keine Daten für {player} im Zeitraum.")

st.divider()

# --- HEAD-TO-HEAD ---
st.write("### ⚔️ Head-to-Head (Tagessiege)")
daily_avg = df_filtered.groupby(['play_date', 'player'])['average'].mean().unstack()

if 'Hanno' in daily_avg.columns and 'Dominik' in daily_avg.columns:
    h2h_df = daily_avg.dropna(subset=['Hanno', 'Dominik'])
    if not h2h_df.empty:
        hanno_wins = (h2h_df['Hanno'] > h2h_df['Dominik']).sum()
        dominik_wins = (h2h_df['Dominik'] > h2h_df['Hanno']).sum()
        draws = (h2h_df['Hanno'] == h2h_df['Dominik']).sum()

        h1, h2, h3 = st.columns(3)
        h1.metric("Hanno", hanno_wins)
        h2.metric("Unentschieden", draws)
        h3.metric("Dominik", dominik_wins)
    else:
        st.info("Keine gemeinsamen Spieltage im Zeitraum.")
else:
    st.info("Zu wenig Daten für den direkten Vergleich.")

st.divider()

# --- APPLE STYLE CHARTS ---
apple_colors = {"Hanno": "#007AFF", "Dominik": "#FF9500"} # iOS Blau und Orange

# 1. Diagramm: Formverlauf über Zeit
st.write("### 📈 Formverlauf (Tages-Schnitt)")
df_daily_chart = df_filtered.groupby(['play_date', 'player'], as_index=False)['average'].mean()
df_daily_chart['Datum'] = df_daily_chart['play_date'].dt.strftime('%d.%m.%Y')
df_daily_chart = df_daily_chart.rename(columns={"average": "3er Schnitt", "player": "Spieler"})

fig_line = px.line(df_daily_chart, x='play_date', y='3er Schnitt', color='Spieler', markers=True, 
                   color_discrete_map=apple_colors, hover_data={"Datum": True, "play_date": False})

fig_line.update_traces(line=dict(width=3), marker=dict(size=8))
fig_line.update_layout(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=""),
    margin=dict(l=0, r=0, t=30, b=0)
)
fig_line.update_xaxes(title="", tickformat="%d.%m.%Y", showgrid=False, zeroline=False)
fig_line.update_yaxes(title="3er Schnitt", showgrid=True, gridcolor='rgba(150,150,150,0.1)', zeroline=False)
st.plotly_chart(fig_line, use_container_width=True)

st.divider()

# 2. Diagramm: Tagesverlauf (Warm-up vs Ermüdung)
st.write("### ⏱️ Tagesverlauf: Warm-up vs. Ermüdung")
st.write("Dieser Chart zeigt den Durchschnittsschnitt pro Lag-Nummer an einem Tag.")

# Chronologische Sortierung anhand der Datenbank-ID (id)
df_filtered = df_filtered.sort_values(by=['play_date', 'id'])
# Dem wievielten Spiel des Tages entspricht der Eintrag? (1, 2, 3...)
df_filtered['spiel_nr'] = df_filtered.groupby(['play_date', 'player']).cumcount() + 1
# Durchschnitt pro Spiel-Nummer berechnen
df_intraday = df_filtered.groupby(['spiel_nr', 'player'], as_index=False)['average'].mean()
df_intraday = df_intraday.rename(columns={"average": "Ø 3er Schnitt", "player": "Spieler", "spiel_nr": "Spiel des Tages"})

fig_intra = px.line(df_intraday, x='Spiel des Tages', y='Ø 3er Schnitt', color='Spieler', markers=True, 
                   color_discrete_map=apple_colors)

fig_intra.update_traces(line=dict(width=3), marker=dict(size=8))
fig_intra.update_layout(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=""),
    margin=dict(l=0, r=0, t=30, b=0),
    xaxis=dict(tickmode='linear', dtick=1) # Zeigt exakt 1, 2, 3 auf der Achse
)
fig_intra.update_xaxes(showgrid=False)
fig_intra.update_yaxes(showgrid=True, gridcolor='rgba(150,150,150,0.1)')
st.plotly_chart(fig_intra, use_container_width=True)
