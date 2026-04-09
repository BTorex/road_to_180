import streamlit as st

st.set_page_config(
    page_title="Road to 180",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

GLOBAL_CSS = """
<style>
:root {
    --bg: #0f1117;
    --surface: rgba(255,255,255,0.06);
    --surface-strong: rgba(255,255,255,0.10);
    --border: rgba(255,255,255,0.10);
    --text: #f5f7fb;
    --muted: #9aa4b2;
    --blue: #4da3ff;
    --orange: #ff9d4d;
    --green: #33d17a;
    --red: #ff6b6b;
    --gold: #f6c453;
}

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(77,163,255,0.12), transparent 28%),
        radial-gradient(circle at top right, rgba(255,157,77,0.10), transparent 26%),
        linear-gradient(180deg, #0b0d12 0%, #11151c 100%);
    color: var(--text);
}

[data-testid="stSidebar"], [data-testid="collapsedControl"] {
    display: none !important;
}

.block-container {
    padding-top: 1.1rem;
    padding-bottom: 2rem;
    max-width: 1240px;
}

.page-title {
    font-size: clamp(1.6rem, 1.2rem + 1.2vw, 2.4rem);
    font-weight: 800;
    letter-spacing: -0.02em;
    margin-bottom: 0.2rem;
}

.page-subtitle {
    color: var(--muted);
    font-size: 0.97rem;
    margin-bottom: 1rem;
}

.section-label {
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-size: 0.72rem;
    font-weight: 700;
    margin-bottom: 0.65rem;
}

.panel {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 22px;
    padding: 1rem 1.05rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.18);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
}

.hero-panel {
    background: linear-gradient(135deg, rgba(255,255,255,0.11), rgba(255,255,255,0.05));
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 24px;
    padding: 1rem 1.1rem;
    box-shadow: 0 16px 38px rgba(0,0,0,0.20);
}

.avatar {
    width: 42px;
    height: 42px;
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    color: white;
}

.avatar-h { background: linear-gradient(135deg, #3c8dff, #60b5ff); }
.avatar-d { background: linear-gradient(135deg, #ff8d3a, #ffb066); }

.small-muted {
    color: var(--muted);
    font-size: 0.82rem;
}

.record-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 20px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.75rem;
}

.rank-chip {
    width: 34px;
    height: 34px;
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    background: rgba(255,255,255,0.08);
}

.rank-top {
    background: linear-gradient(135deg, #f6c453, #ffde7a);
    color: #262626;
}

[data-testid="stMetric"] {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 20px;
    padding: 0.85rem 1rem;
    box-shadow: 0 10px 25px rgba(0,0,0,0.16);
}

[data-testid="stMetricLabel"] { color: var(--muted); }
[data-testid="stMetricValue"] { font-weight: 800; letter-spacing: -0.03em; }

.stButton > button, .stDownloadButton > button {
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.10);
    background: rgba(255,255,255,0.08);
    color: white;
    min-height: 2.8rem;
    font-weight: 700;
}

.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: rgba(255,255,255,0.18);
    background: rgba(255,255,255,0.12);
}

.stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] > div, textarea {
    border-radius: 16px !important;
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
}

div[data-baseweb="tab-list"] { gap: 0.45rem; }
a[role="tab"] {
    border-radius: 14px !important;
    background: rgba(255,255,255,0.05) !important;
    padding: 0.45rem 0.9rem !important;
}
a[aria-selected="true"] { background: rgba(255,255,255,0.14) !important; }
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

pages = [
    st.Page("pages/1_eingabe.py", title="Eingabe", icon="✍️", default=True),
    st.Page("pages/2_statistiken.py", title="Statistiken", icon="📊"),
    st.Page("pages/3_rekorde.py", title="Rekorde", icon="🏆"),
]

pg = st.navigation(pages, position="top")
pg.run()
