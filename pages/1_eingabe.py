import streamlit as st
import pandas as pd
from supabase import create_client

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# Neuer Titel und Untertitel
st.title("🎯 Road to 180")
st.subheader("Darts-Tracker")

# Datumsauswahl im deutschen Format
selected_date = st.date_input("Spieldatum auswählen", format="DD.MM.YYYY")

st.write("### Neue Averages eintragen")
col1, col2 = st.columns(2)

with col1:
    st.write("#### Hanno")
    hanno_avg = st.number_input("3er Schnitt Hanno", min_value=0.0, max_value=180.0, step=0.1)
    if st.button("Für Hanno speichern"):
        supabase.table("dart_averages").insert({"play_date": str(selected_date), "player": "Hanno", "average": hanno_avg}).execute()
        st.success(f"Gespeichert! (Schnitt: {hanno_avg})")

with col2:
    st.write("#### Dominik")
    dominik_avg = st.number_input("3er Schnitt Dominik", min_value=0.0, max_value=180.0, step=0.1)
    if st.button("Für Dominik speichern"):
        supabase.table("dart_averages").insert({"play_date": str(selected_date), "player": "Dominik", "average": dominik_avg}).execute()
        st.success(f"Gespeichert! (Schnitt: {dominik_avg})")

st.divider()
st.subheader("📊 Unsere Historie")
response = supabase.table("dart_averages").select("*").order("play_date", desc=True).execute()

if response.data:
    df = pd.DataFrame(response.data)
    
    # Datum in deutsches Format umwandeln (TT.MM.JJJJ)
    df['play_date'] = pd.to_datetime(df['play_date']).dt.strftime('%d.%m.%Y')
    
    # Sprechende Spaltennamen für die Tabelle
    df_display = df.rename(columns={
        "play_date": "Datum",
        "player": "Spieler",
        "average": "3er Schnitt"
    })
    
    # Tabelle anzeigen (ohne störenden Index)
    st.dataframe(df_display[["Datum", "Spieler", "3er Schnitt"]], use_container_width=True, hide_index=True)
