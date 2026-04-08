import streamlit as st

# 1. Page Config (muss zwingend in Zeile 1 stehen)
st.set_page_config(
    page_title="Road to 180", 
    page_icon="🎯", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# 2. Globales Apple UI/UX Design (CSS)
st.markdown("""
<style>
    /* System-Schriftarten (San Francisco / Apple-Standard) */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
    }
    
    /* Elegante, zentrierte Apple-Header */
    .apple-header {
        text-align: center; font-weight: 700; font-size: 2.8rem;
        letter-spacing: -0.02em; margin-bottom: 0px; padding-bottom: 0px;
    }
    .apple-subheader {
        text-align: center; color: #86868b; font-size: 1.3rem; font-weight: 400; margin-top: 5px;
    }
    .powered-by {
        text-align: center; color: #c8c8cc; font-size: 0.75rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 1.5px; margin-top: 8px; margin-bottom: 35px;
    }
    
    /* iOS Widget Style für die Metriken/KPIs */
    [data-testid="stMetric"] {
        background-color: #ffffff; border-radius: 18px; padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04); border: 1px solid rgba(0,0,0,0.03);
    }
    /* Dark Mode Anpassung */
    @media (prefers-color-scheme: dark) {
        [data-testid="stMetric"] {
            background-color: #1c1c1e; border: 1px solid rgba(255,255,255,0.05);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        }
    }
</style>
""", unsafe_allow_html=True)

# 3. Globaler Header (wird auf JEDER Seite oben angezeigt)
st.markdown("<div class='apple-header'>🎯 Road to 180</div>", unsafe_allow_html=True)
st.markdown("<div class='apple-subheader'>Darts-Tracker</div>", unsafe_allow_html=True)
st.markdown("<div class='powered-by'>powered by Adebar</div>", unsafe_allow_html=True)

# 4. Navigation konfigurieren (inklusive neuer Rekord-Seite)
eingabe_page = st.Page("pages/1_eingabe.py", title="Averages eintragen", icon="✍️")
statistik_page = st.Page("pages/2_statistiken.py", title="Statistiken & Analyse", icon="📊")
rekorde_page = st.Page("pages/3_rekorde.py", title="All-Time Highs", icon="🏆")

pg = st.navigation([eingabe_page, statistik_page, rekorde_page])
pg.run()
