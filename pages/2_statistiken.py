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

st.title("🎯 Road to 180")
st.subheader("Darts-Tracker: Professionelle Auswertung")

response = supabase.table("dart_averages").select("*").order("play_date").execute()

if not response.data:
    st.info("Noch keine Daten vorhanden. Tragt zuerst ein paar Averages ein!")
    st.stop()

df = pd.DataFrame(response.data)
df['play_date'] = pd.to_datetime(df['play_date'])

# --- DATUMSFILTER ---
st.write("### 📅 Zeitraum filtern")
min_date = df['play_date'].min().date()
max_date = df['play_date'].max().date()

date_selection = st.date_input(
    "Wähle den Zeitraum:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    format="DD.MM.YYYY"
)

# Daten filtern basierend auf Auswahl
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

# --- KPIs ---
st.subheader("🏆 Key Performance Indicators (KPIs)")
col1, col2 = st.columns(2)

for idx, player in enumerate(["Hanno", "Dominik"]):
    player_df = df_filtered[df_filtered['player'] == player].copy()
    
    with (col1 if idx == 0 else col2):
        st.write(f"### 🎯 {player}")
        if not player_df.empty:
            avg_alltime = player_df['average'].mean()
            max_avg = player_df['average'].max()
            std_dev = player_df['average'].std()
            games_played = len(player_df)
            
            # Trend: Letzte 5 Spiele
            trend_avg = player_df['average'].tail(5).mean() if games_played >= 5 else avg_alltime
            
            m1, m2 = st.columns(2)
            m1.metric("Gesamtschnitt", f"{avg_alltime:.2f}")
            m2.metric("Höchster Schnitt", f"{max_avg:.2f}")
            
            m3, m4 = st.columns(2)
            m3.metric("Form (Letzte 5)", f"{trend_avg:.2f}" if games_played >= 5 else "-")
            std_str = f"± {std_dev:.2f}" if pd.notna(std_dev) else "-"
            m4.metric("Konstanz (Streuung)", std_str, help="Je niedriger der Wert, desto konstanter.")
            
            st.caption(f"Spiele im Zeitraum: {games_played}")
        else:
            st.write("Keine Spiele im Zeitraum.")

st.divider()

# --- HEAD-TO-HEAD ---
st.subheader("⚔️ Head-to-Head (Tagessiege)")
st.write("Wer hat an gemeinsamen Spieltagen den besseren Tages-Schnitt geworfen?")

# Tagesdurchschnitt berechnen, falls jemand mehrfach am Tag eingetragen wurde
daily_avg = df_filtered.groupby(['play_date', 'player'])['average'].mean().unstack()

if 'Hanno' in daily_avg.columns and 'Dominik' in daily_avg.columns:
    h2h_df = daily_avg.dropna(subset=['Hanno', 'Dominik'])
    if not h2h_df.empty:
        hanno_wins = (h2h_df['Hanno'] > h2h_df['Dominik']).sum()
        dominik_wins = (h2h_df['Dominik'] > h2h_df['Hanno']).sum()
        draws = (h2h_df['Hanno'] == h2h_df['Dominik']).sum()

        h1, h2, h3 = st.columns(3)
        h1.metric("Siege Hanno", hanno_wins)
        h2.metric("Unentschieden", draws)
        h3.metric("Siege Dominik", dominik_wins)
    else:
        st.info("Keine gemeinsamen Spieltage im Zeitraum.")
else:
    st.info("Zu wenig Daten für den direkten Vergleich.")

st.divider()

# --- CHARTS ---
st.subheader("📈 Entwicklung über Zeit")

# Hilfsspalte für den deutschen Datums-Hover im Diagramm
df_filtered['Datum'] = df_filtered['play_date'].dt.strftime('%d.%m.%Y')
df_filtered = df_filtered.rename(columns={"average": "3er Schnitt", "player": "Spieler"})

fig_line = px.line(df_filtered, x='play_date', y='3er Schnitt', color='Spieler', markers=True, 
                   hover_data={"Datum": True, "play_date": False})
fig_line.update_traces(line=dict(width=3), marker=dict(size=8))
fig_line.update_xaxes(title="Datum", tickformat="%d.%m.%Y")
st.plotly_chart(fig_line, use_container_width=True)

st.subheader("🎯 Konstanz-Analyse (Boxplot)")
st.write("Zeigt die Streuung eurer Würfe. Eine kompakte Box bedeutet hohe Konstanz (wenig Schwankung).")
fig_box = px.box(df_filtered, x='Spieler', y='3er Schnitt', color='Spieler', 
                 hover_data={"Datum": True})
st.plotly_chart(fig_box, use_container_width=True)
