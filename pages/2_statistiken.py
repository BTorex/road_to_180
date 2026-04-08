import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from supabase import create_client

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

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
    "Auswahl", value=(min_date, max_date), min_value=min_date, max_value=max_date,
    format="DD.MM.YYYY", label_visibility="collapsed"
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

# --- UMFANGREICHE KPIs & GAMIFICATION ---
st.write("### 🏆 Performance-Analyse")
tab1, tab2 = st.tabs(["🎯 Hanno", "🎯 Dominik"])

for tab, player in zip([tab1, tab2], ["Hanno", "Dominik"]):
    with tab:
        player_df = df_filtered[df_filtered['player'] == player].copy()
        
        if not player_df.empty:
            avg_mean = player_df['average'].mean()
            avg_median = player_df['average'].median()
            max_avg = player_df['average'].max()
            games_played = len(player_df)
            
            top_10_percent_count = max(1, int(games_played * 0.10))
            a_game_avg = player_df.nlargest(top_10_percent_count, 'average')['average'].mean()
            
            # Form-Trend
            form_avg = player_df['average'].tail(5).mean() if games_played >= 5 else avg_mean
            form_delta = form_avg - avg_mean

            # Gamification Logic
            badge, badge_text, badge_color = "🎯", "Solide Form", "#888"
            if form_delta >= 3.0:
                badge, badge_text, badge_color = "🔥", "On Fire!", "#FF3B30"
            elif form_delta <= -3.0:
                badge, badge_text, badge_color = "🧊", "Ice Cold", "#007AFF"
            if games_played > 0 and player_df.iloc[-1]['average'] == max_avg:
                badge, badge_text, badge_color = "🚀", "Peak Performance", "#FF9500"

            # Avatar & Badge UI
            avatar_class = "avatar-h" if player == "Hanno" else "avatar-d"
            letter = "H" if player == "Hanno" else "D"
            st.markdown(f"""
            <div style='display:flex; flex-direction:column; align-items:center; margin-bottom: 20px;'>
                <div class='avatar {avatar_class}'>{letter}</div>
                <div style='margin-top: 10px; background: rgba(0,0,0,0.05); padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.9rem; color: {badge_color}; border: 1px solid rgba(0,0,0,0.05);'>
                    {badge} {badge_text}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.caption(f"Spiele im Zeitraum: {games_played}")
            
            # Mobile-optimized Columns
            c1, c2 = st.columns(2)
            c1.metric("Ø Gesamtschnitt", f"{avg_mean:.2f}")
            c2.metric("Median (Typisch)", f"{avg_median:.2f}")
            
            c3, c4 = st.columns(2)
            c3.metric("Aktuelle Form (Letzte 5)", f"{form_avg:.2f}", delta=f"{form_delta:.2f}", delta_color="normal")
            c4.metric("A-Game (Top 10%)", f"{a_game_avg:.2f}")
            
        else:
            st.info(f"Keine Daten für {player} im Zeitraum.")

st.divider()

# --- HEAD-TO-HEAD & WIN STREAK ---
st.write("### ⚔️ Head-to-Head & Streaks")

daily_avg = df_filtered.groupby(['play_date', 'player'])['average'].mean().unstack()

if 'Hanno' in daily_avg.columns and 'Dominik' in daily_avg.columns:
    h2h_df = daily_avg.dropna(subset=['Hanno', 'Dominik']).sort_index()
    if not h2h_df.empty:
        # Gewinner pro Tag bestimmen
        conditions = [h2h_df['Hanno'] > h2h_df['Dominik'], h2h_df['Dominik'] > h2h_df['Hanno']]
        h2h_df['winner'] = np.select(conditions, ['Hanno', 'Dominik'], default='Draw')
        
        hanno_wins = (h2h_df['winner'] == 'Hanno').sum()
        dominik_wins = (h2h_df['winner'] == 'Dominik').sum()
        draws = (h2h_df['winner'] == 'Draw').sum()

        # Streak Berechnung
        winners_list = h2h_df['winner'].tolist()
        current_streak_player = winners_list[-1]
        streak_count = 0
        if current_streak_player != 'Draw':
            for w in reversed(winners_list):
                if w == current_streak_player:
                    streak_count += 1
                else:
                    break

        h1, h2, h3 = st.columns(3)
        h1.metric("Siege Hanno", hanno_wins)
        h2.metric("Unentschieden", draws)
        h3.metric("Siege Dominik", dominik_wins)

        if current_streak_player != 'Draw':
            st.success(f"🔥 Aktuelle Siegesserie (Tagessiege): **{current_streak_player}** mit **{streak_count}** in Folge!")
        else:
            st.info("Letzter gemeinsamer Spieltag endete Unentschieden.")
    else:
        st.info("Keine gemeinsamen Spieltage im Zeitraum.")

st.divider()

# --- APPLE STYLE CHARTS ---
apple_colors = {"Hanno": "#007AFF", "Dominik": "#FF9500"}

# NEU: Gleitender Durchschnitt (Rolling Average)
st.write("### 🌊 Form-Kurve (Gleitender Durchschnitt)")
st.write("Zeigt den Durchschnitt der letzten 10 Spiele, um eure wahre Form (Trend) ohne Ausreißer zu visualisieren.")

df_ma = df_filtered.sort_values(by=['play_date', 'id']).copy()
df_ma['spiel_total_nr'] = df_ma.groupby('player').cumcount() + 1
df_ma['Rolling'] = df_ma.groupby('player')['average'].transform(lambda x: x.rolling(window=10, min_periods=1).mean())

fig_ma = px.line(df_ma, x='spiel_total_nr', y='Rolling', color='player',
                 color_discrete_map=apple_colors, labels={'spiel_total_nr': 'Spiel Nummer (Gesamt)', 'Rolling': 'Ø Letzte 10 Spiele'})
fig_ma.update_traces(line=dict(width=4))
fig_ma.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                     legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=""),
                     margin=dict(l=10, r=10, t=30, b=10)) # Mobile margin fix
fig_ma.update_xaxes(showgrid=False)
fig_ma.update_yaxes(showgrid=True, gridcolor='rgba(150,150,150,0.1)')
st.plotly_chart(fig_ma, use_container_width=True)

st.divider()

# Diagramm: Tagesverlauf (Warm-up vs Ermüdung)
st.write("### ⏱️ Tagesverlauf: Warm-up vs. Ermüdung")
df_intraday = df_filtered.copy()
df_intraday['spiel_nr'] = df_intraday.groupby(['play_date', 'player']).cumcount() + 1
df_intra_grouped = df_intraday.groupby(['spiel_nr', 'player'], as_index=False)['average'].mean()

fig_intra = px.line(df_intra_grouped, x='spiel_nr', y='average', color='player', markers=True, 
                   color_discrete_map=apple_colors, labels={'spiel_nr': 'Spiel des Tages', 'average': 'Ø 3er Schnitt'})
fig_intra.update_traces(line=dict(width=3), marker=dict(size=8))
fig_intra.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=""),
    margin=dict(l=10, r=10, t=30, b=10), xaxis=dict(tickmode='linear', dtick=1))
fig_intra.update_xaxes(showgrid=False)
fig_intra.update_yaxes(showgrid=True, gridcolor='rgba(150,150,150,0.1)')
st.plotly_chart(fig_intra, use_container_width=True)

st.divider()

# --- DETAILTABELLE MIT KOMMENTAREN ---
st.write("### 📋 Alle Spiele im Zeitraum")
if 'comment' not in df_filtered.columns: df_filtered['comment'] = ""
df_table = df_filtered.sort_values(by=['play_date', 'id'], ascending=[False, False])
df_table['Datum'] = df_table['play_date'].dt.strftime('%d.%m.%Y')
df_table['Kommentar'] = df_table['comment'].fillna("")

st.dataframe(df_table[["Datum", "player", "average", "Kommentar"]].rename(columns={"player": "Spieler", "average": "Schnitt"}), 
             use_container_width=True, hide_index=True)
