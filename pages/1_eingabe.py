import streamlit as st
import pandas as pd
from supabase import create_client

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

st.write("### 📅 Neuer Eintrag")
# Datumsauswahl kompakt halten
selected_date = st.date_input("Spieldatum", format="DD.MM.YYYY", label_visibility="collapsed")

# Mobile-Optimierung: Tabs
tab1, tab2 = st.tabs(["🎯 Hanno", "🎯 Dominik"])

with tab1:
    hanno_avg = st.number_input("Schnitt (Hanno)", min_value=0.0, max_value=180.0, step=0.1, key="h_avg")
    if st.button("Speichern für Hanno", use_container_width=True, type="primary"):
        supabase.table("dart_averages").insert({"play_date": str(selected_date), "player": "Hanno", "average": hanno_avg}).execute()
        st.success(f"Gespeichert! ({hanno_avg})")

with tab2:
    dominik_avg = st.number_input("Schnitt (Dominik)", min_value=0.0, max_value=180.0, step=0.1, key="d_avg")
    if st.button("Speichern für Dominik", use_container_width=True, type="primary"):
        supabase.table("dart_averages").insert({"play_date": str(selected_date), "player": "Dominik", "average": dominik_avg}).execute()
        st.success(f"Gespeichert! ({dominik_avg})")

st.divider()

st.write("### 📊 Letzte 10 Einträge")

# Sortierung nach der Datenbank-ID garantiert, dass wirklich die zuletzt eingetippten Werte oben stehen
response = supabase.table("dart_averages").select("*").order("id", desc=True).limit(10).execute()

if response.data:
    df = pd.DataFrame(response.data)
    df['play_date'] = pd.to_datetime(df['play_date']).dt.strftime('%d.%m.%Y')
    df_display = df.rename(columns={"play_date": "Datum", "player": "Spieler", "average": "3er Schnitt"})
    
    st.dataframe(df_display[["Datum", "Spieler", "3er Schnitt"]], use_container_width=True, hide_index=True)
