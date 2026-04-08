import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Supabase Verbindung herstellen und cachen
@st.cache_resource
def init_connection():
    url = st.secrets["https://msthrejgamerrxipnehe.supabase.co"]
    key = st.secrets["sb_publishable_kpMJpqn2LbDTfFzr0Pk1cw_FK6pr4xy"]
    return create_client(url, key)

supabase = init_connection()

st.title("🎯 Darts Tracker: Hanno & Dominik")

# Datumsauswahl
selected_date = st.date_input("Spieldatum auswählen")

st.subheader("Neue Averages eintragen")
col1, col2 = st.columns(2)

# Eingabe für Hanno
with col1:
    st.write("### Hanno")
    hanno_avg = st.number_input("3er Schnitt Hanno", min_value=0.0, max_value=180.0, step=0.1)
    if st.button("Für Hanno speichern"):
        supabase.table("dart_averages").insert({"play_date": str(selected_date), "player": "Hanno", "average": hanno_avg}).execute()
        st.success(f"Hannos Schnitt ({hanno_avg}) gespeichert!")

# Eingabe für Dominik
with col2:
    st.write("### Dominik")
    dominik_avg = st.number_input("3er Schnitt Dominik", min_value=0.0, max_value=180.0, step=0.1)
    if st.button("Für Dominik speichern"):
        supabase.table("dart_averages").insert({"play_date": str(selected_date), "player": "Dominik", "average": dominik_avg}).execute()
        st.success(f"Dominiks Schnitt ({dominik_avg}) gespeichert!")

# Bisherige Einträge anzeigen
st.subheader("📊 Unsere Historie")
response = supabase.table("dart_averages").select("*").order("play_date").execute()

if response.data:
    df = pd.DataFrame(response.data)
    # Formatiert die Ansicht der Tabelle
    st.dataframe(df[["play_date", "player", "average"]], use_container_width=True)
