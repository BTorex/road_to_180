import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from supabase import create_client

# --- APPLE UI/UX DESIGN (CSS) ---
st.markdown("""
<style>
    /* System-Schriftarten im Apple-Style erzwingen */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Elegante, zentrierte Apple-Header */
    .apple-header {
        text-align: center;
        font-weight: 700;
        font-size: 2.8rem;
        letter-spacing: -0.02em;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    .apple-subheader {
        text-align: center;
        color: #86868b;
        font-size: 1.3rem;
        font-weight: 400;
        margin-top: 5px;
    }
    .powered-by {
        text-align: center;
        color: #c8c8cc;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 8px;
        margin-bottom: 40px;
    }
    
    /* iOS Widget Style für die KPIs */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        border: 1px solid rgba(0,0,0,0.03);
    }
    /* Anpassung für den Dark Mode (falls jemand den Streamlit Dark Mode nutzt) */
    @media (prefers-color-scheme: dark) {
        [data-testid="stMetric"] {
            background-color: #1c1c1e;
            border: 1px solid rgba(255,255,255,0.05);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        }
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<div class='apple-header'>🎯 Road to 180</div>", unsafe_allow_html=True)
st.markdown("<div class='apple-subheader'>Darts-Tracker</div>", unsafe_allow_html=True)
st.markdown("<div class='powered-by'>powered by Adebar</div>", unsafe_allow_html=True)

# --- DATENBANK VERBINDUNG ---
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
        player_df = df_filtered[df_filtered['player'] == player].copy()
        
        if not player_df.empty:
            # Berechnungen
            avg_mean = player_df['average'].mean()
            avg_median = player_df['average'].median()
            max_avg = player_df['average'].max()
            min_avg = player_df['average'].min()
            std_dev = player_df['average'].std()
            games_played = len(player_df)
            
            # A-Game (Top 10% Schnitt)
            top_10_percent_count = max(1, int(games_played * 0.10))
            a_game_avg = player_df.nlargest(top_10_percent_count, 'average')['average'].mean()
            
            # Form (Letzte 5 Spiele) & Delta
            if games_played >= 5:
                form_avg = player_df['average'].tail(5).mean()
                form_delta = form_avg - avg_mean
            else:
                form_avg = avg_mean
                form_delta = 0.0

            # UI Rendering (Karten-Raster)
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
            
            st.write("") # Spacer
        else:
            st.info(f"Keine Daten für {player} in diesem Zeitraum.")

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

st.divider()

# --- APPLE STYLE CHARTS ---
st.write("### 📈 Formverlauf (Tages-Schnitt)")

df_daily_chart = df_filtered.groupby(['play_date', 'player'], as_index=False)['average'].mean()
df_daily_chart['Datum'] = df_daily_chart['play_date'].dt.strftime('%d.%m.%Y')
df_daily_chart = df_daily_chart.rename(columns={"average": "3er Schnitt", "player": "Spieler"})

# Apple-ähnliche Farbpalette
apple_colors = {"Hanno": "#007AFF", "Dominik": "#FF9500"} # iOS Blau und iOS Orange

fig_line = px.line(df_daily_chart, x='play_date', y='3er Schnitt', color='Spieler', markers=True, 
                   color_discrete_map=apple_colors,
                   hover_data={"Datum": True, "play_date": False})

fig_line.update_traces(line=dict(width=3), marker=dict(size=8))
fig_line.update_layout(
    plot_bgcolor="rgba(0,0,0,0)", # Transparenter Hintergrund
    paper_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=""),
    margin=dict(l=0, r=0, t=30, b=0)
)
fig_line.update_xaxes(title="", tickformat="%d.%m.%Y", showgrid=False, zeroline=False)
fig_line.update_yaxes(title="3er Schnitt", showgrid=True, gridcolor='rgba(150,150,150,0.1)', zeroline=False)

st.plotly_chart(fig_line, use_container_width=True)
