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

st.title("📊 Performance & Statistiken")

# Daten aus Supabase abrufen
response = supabase.table("dart_averages").select("*").order("play_date").execute()

if not response.data:
    st.info("Noch keine Daten vorhanden. Tragt zuerst ein paar Averages ein!")
    st.stop()

# Datenaufbereitung mit Pandas
df = pd.DataFrame(response.data)
df['play_date'] = pd.to_datetime(df['play_date'])

st.subheader("🏆 Key Performance Indicators")
col1, col2 = st.columns(2)

# KPIs für beide Spieler berechnen
for idx, player in enumerate(["Hanno", "Dominik"]):
    player_df = df[df['player'] == player]
    
    with (col1 if idx == 0 else col2):
        st.write(f"### {player}")
        if not player_df.empty:
            avg_alltime = player_df['average'].mean()
            max_avg = player_df['average'].max()
            games_played = len(player_df)
            
            st.metric("Gesamtschnitt", f"{avg_alltime:.2f}")
            st.metric("Höchster Schnitt", f"{max_avg:.2f}")
            st.caption(f"Basierend auf {games_played} Einträgen")
        else:
            st.write("Noch keine Spiele.")

st.divider()

# Liniendiagramm: Verlauf über Zeit
st.subheader("📈 Entwicklung über Zeit")
fig_line = px.line(df, x='play_date', y='average', color='player', markers=True, 
                   title="3er Schnitt Verlauf", labels={"play_date": "Datum", "average": "3er Schnitt", "player": "Spieler"})
fig_line.update_traces(line=dict(width=3), marker=dict(size=8))
st.plotly_chart(fig_line, use_container_width=True)

# Boxplot: Konstanz / Streuung
st.subheader("🎯 Konstanz (Streuung der Würfe)")
st.write("Ein kleinerer Boxplot bedeutet, dass der Spieler konstanter wirft. Ausreißer nach oben oder unten werden als einzelne Punkte dargestellt.")
fig_box = px.box(df, x='player', y='average', color='player', 
                 title="Verteilung der Averages", labels={"average": "3er Schnitt", "player": "Spieler"})
st.plotly_chart(fig_box, use_container_width=True)
