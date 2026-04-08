import streamlit as st

st.set_page_config(page_title="Road to 180", page_icon="🎯", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* iOS System Font & Smooth Scrolling */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
        -webkit-font-smoothing: antialiased;
    }
    
    /* Next-Level Header */
    .apple-header {
        text-align: center; font-weight: 800; font-size: 3rem;
        background: -webkit-linear-gradient(45deg, #1a1a1a, #4a4a4a);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        letter-spacing: -0.03em; margin-bottom: 0px; padding-bottom: 0px;
    }
    @media (prefers-color-scheme: dark) {
        .apple-header { background: -webkit-linear-gradient(45deg, #ffffff, #a0a0a0); -webkit-background-clip: text; }
    }
    .apple-subheader { text-align: center; color: #86868b; font-size: 1.2rem; font-weight: 500; margin-top: 5px; }
    .powered-by { text-align: center; color: #c8c8cc; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; margin-top: 8px; margin-bottom: 35px; }
    
    /* Glassmorphism Cards für KPIs */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 20px; padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.4);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px); box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
    }
    @media (prefers-color-scheme: dark) {
        [data-testid="stMetric"] {
            background: rgba(30, 30, 30, 0.6); border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
    }

    /* Stilisierte Avatar Logos */
    .avatar-container { display: flex; justify-content: center; margin-bottom: 15px; }
    .avatar {
        display: flex; align-items: center; justify-content: center;
        width: 60px; height: 60px; border-radius: 22px; /* Apple Squircle */
        color: white; font-weight: 800; font-size: 28px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
    }
    .avatar-h { background: linear-gradient(135deg, #00C6FF, #0072FF); } /* Hanno: Neon Blue */
    .avatar-d { background: linear-gradient(135deg, #FFD200, #F7971E); } /* Dominik: Sunset Orange */
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='apple-header'>Road to 180</div>", unsafe_allow_html=True)
st.markdown("<div class='apple-subheader'>Pro Darts-Tracker</div>", unsafe_allow_html=True)
st.markdown("<div class='powered-by'>powered by Adebar</div>", unsafe_allow_html=True)

eingabe_page = st.Page("pages/1_eingabe.py", title="Averages eintragen", icon="✍️")
statistik_page = st.Page("pages/2_statistiken.py", title="Statistiken & Analyse", icon="📊")
rekorde_page = st.Page("pages/3_rekorde.py", title="All-Time Highs", icon="🏆")

pg = st.navigation([eingabe_page, statistik_page, rekorde_page])
pg.run()
