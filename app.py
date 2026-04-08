import streamlit as st

# Mobile-Optimierung: Sidebar standardmäßig einklappen und Layout zentrieren
st.set_page_config(
    page_title="Road to 180", 
    page_icon="🎯", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

eingabe_page = st.Page("pages/1_eingabe.py", title="Averages eintragen", icon="🎯")
statistik_page = st.Page("pages/2_statistiken.py", title="Statistiken & Analyse", icon="📊")

pg = st.navigation([eingabe_page, statistik_page])
pg.run()
