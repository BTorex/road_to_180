import streamlit as st
import pandas as pd
from supabase import create_client

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

st.title("🎯 Road to 180")
st.subheader("Darts-Tracker")

selected_date = st.date_input("📅 Spieldatum", format="DD.MM.YYYY")

st.write("### ✍️ Averages eintragen")

# Mobile-Optimierung: Tabs statt Spalten
tab1, tab2 = st.tabs(["🎯 Hanno", "🎯 Dominik"])

with tab1:
    hanno_avg = st.number_input("Schnitt (Hanno)", min_value=0.0, max_value=180.0, step=0.1, key="h_avg")
    # Mobile-Optimierung: Großer Button
    if st.button("Speichern für Hanno", use_container_width=True, type="primary"):
        supabase.table("dart_averages").insert({"play_date": str(selected_date), "player": "Hanno", "average": hanno_avg}).execute()
        st.success(f"Gespeichert! ({hanno_avg})")

with tab2:
    dominik_avg = st.number_input("Schnitt (Dominik)", min_value=0.0, max_value=180.0, step=0.1, key="d_avg")
    if st.button("Speichern für Dominik", use_container_width=True, type="primary"):
        supabase.table("dart_averages").insert({"play_date": str(selected_date), "player": "Dominik", "average": dominik_avg}).execute()
        st.success(f"Gespeichert! ({dominik_avg})")

st.divider()
st.subheader("📊 Letzte Einträge")

# Mobile-Optimierung: Nur die letzten 10 Einträge laden, um endloses Scrollen zu vermeiden
response = supabase.table("dart_averages").select("*").order("play_date", desc=True).limit(10).execute()

if response.data:
    df = pd.DataFrame(response.data)
    df['play_date'] = pd.to_datetime(df['play_date']).dt.strftime('%d.%m.%Y')
    df_display = df.rename(columns={"play_date": "Datum", "player": "Spieler", "average": "3er Schnitt"})
    st.dataframe(df_display[["Datum", "Spieler", "3er Schnitt"]], use_container_width=True, hide_index=True)
