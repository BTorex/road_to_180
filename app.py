
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Road to 180",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ROOT = Path(__file__).parent
STATIC = ROOT / "static"
LOGO = STATIC / "logo.png"
HEADER = STATIC / "header.png"

if LOGO.exists():
    st.logo(str(LOGO), size="large")

st.markdown("""
<style>
:root {
    --text: #f5f7fb;
    --muted: #9aa4b2;
}
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif;
}
.stApp {
    background:
        radial-gradient(circle at top left, rgba(90,168,255,0.13), transparent 28%),
        radial-gradient(circle at top right, rgba(255,171,102,0.11), transparent 26%),
        linear-gradient(180deg, #090b10 0%, #11151c 100%);
    color: var(--text);
}
header[data-testid="stHeader"] {
    background: rgba(9, 11, 16, 0.78) !important;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
}
[data-testid="stSidebar"], [data-testid="collapsedControl"] {
    display: none !important;
}
.block-container {
    padding-top: 5.9rem !important;
    padding-bottom: 2rem !important;
    max-width: 1180px;
}
@media (max-width: 768px) {
    .block-container {
        padding-top: 6.5rem !important;
        padding-left: 0.9rem !important;
        padding-right: 0.9rem !important;
        max-width: 100%;
    }
    div[data-testid="stHorizontalBlock"] {
        display: flex;
        flex-direction: column;
        gap: 0.8rem;
    }
}
.page-title {
    font-size: clamp(1.45rem, 1.15rem + 1vw, 2.25rem);
    font-weight: 800;
    letter-spacing: -0.02em;
    margin-bottom: 0.2rem;
    line-height: 1.1;
}
.page-subtitle {
    color: var(--muted);
    font-size: 0.98rem;
    margin-bottom: 0.9rem;
}
.section-label {
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-size: 0.72rem;
    font-weight: 700;
    margin-bottom: 0.65rem;
}
.hero-panel {
    background: linear-gradient(135deg, rgba(255,255,255,0.11), rgba(255,255,255,0.05));
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 24px;
    padding: 1rem 1.05rem;
    box-shadow: 0 14px 34px rgba(0,0,0,0.20);
}
.record-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 20px;
    padding: 0.95rem 1rem;
    margin-bottom: 0.8rem;
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
.avatar-fallback {
    width: 46px;
    height: 46px;
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    color: white;
}
.avatar-h { background: linear-gradient(135deg, #3c8dff, #60b5ff); }
.avatar-d { background: linear-gradient(135deg, #ff8d3a, #ffb066); }
.small-muted { color: var(--muted); font-size: 0.82rem; }
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
    min-height: 2.9rem;
    font-weight: 700;
}
.stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] > div, textarea {
    border-radius: 16px !important;
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
}
div[data-baseweb="tab-list"] { gap: 0.45rem; flex-wrap: wrap; }
a[role="tab"] {
    border-radius: 14px !important;
    background: rgba(255,255,255,0.05) !important;
    padding: 0.45rem 0.9rem !important;
}
a[aria-selected="true"] { background: rgba(255,255,255,0.14) !important; }
</style>
""", unsafe_allow_html=True)

if HEADER.exists():
    st.image(str(HEADER), use_container_width=True)

pages = [
    st.Page("pages/1_eingabe.py", title="Eingabe", icon="✍️", default=True),
    st.Page("pages/2_statistiken.py", title="Statistiken", icon="📊"),
    st.Page("pages/3_rekorde.py", title="Rekorde", icon="🏆"),
]
st.navigation(pages, position="top").run()
