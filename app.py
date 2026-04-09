
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
    --bg: #1C1C1E;
    --bg-soft: #232326;
    --card: rgba(255,255,255,0.08);
    --card-strong: rgba(255,255,255,0.12);
    --border: rgba(255,255,255,0.10);
    --text: #f5f5f7;
    --muted: #a1a1aa;
    --red: #FF3B30;
    --red-soft: #ff6b63;
    --green: #34C759;
    --green-soft: #62dd84;
}
html, body, [class*="css"] {
    font-family: Inter, "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.stApp {
    background:
        radial-gradient(circle at top left, rgba(255,59,48,0.16), transparent 28%),
        radial-gradient(circle at top right, rgba(52,199,89,0.12), transparent 22%),
        linear-gradient(180deg, #111113 0%, #1C1C1E 100%);
    color: var(--text);
}
header[data-testid="stHeader"] {
    background: rgba(17, 17, 19, 0.72) !important;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
}
[data-testid="stSidebar"], [data-testid="collapsedControl"] {
    display: none !important;
}
.block-container {
    padding-top: 5.7rem !important;
    padding-bottom: 2rem !important;
    max-width: 1180px;
}
@media (max-width: 768px) {
    .block-container {
        padding-top: 6.2rem !important;
        padding-left: .9rem !important;
        padding-right: .9rem !important;
        max-width: 100%;
    }
    div[data-testid="stHorizontalBlock"] {
        display: flex;
        flex-direction: column;
        gap: .8rem;
    }
    .mini-grid {
        grid-template-columns: 1fr !important;
    }
}
.page-title {
    font-size: clamp(1.6rem, 1.2rem + 1vw, 2.5rem);
    font-weight: 850;
    letter-spacing: -0.03em;
    margin-bottom: .35rem;
    line-height: 1.05;
}
.page-subtitle, .small-muted {
    color: var(--muted);
    font-size: .9rem;
}
.section-label, .kicker {
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: .14em;
    font-size: .72rem;
    font-weight: 800;
    margin-bottom: .55rem;
}
.hero-panel, .glass-card, .input-shell, .record-card, .empty-state {
    background: linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0.05));
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 24px;
    box-shadow: 0 18px 40px rgba(0,0,0,0.22);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
}
.hero-panel, .glass-card, .input-shell, .empty-state {
    padding: 1rem 1.05rem;
    margin-bottom: 1rem;
}
.record-card {
    padding: .95rem 1rem;
    margin-bottom: .8rem;
}
.hero-kpi {
    background: linear-gradient(135deg, rgba(255,59,48,0.18), rgba(52,199,89,0.10));
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 26px;
    padding: 1.15rem;
    box-shadow: 0 16px 36px rgba(0,0,0,0.22);
    margin-bottom: 1rem;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
}
.records-hero {
    background: linear-gradient(135deg, rgba(255,59,48,0.18), rgba(255,255,255,0.06));
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 28px;
    padding: 1.15rem 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 18px 44px rgba(0,0,0,0.24);
    backdrop-filter: blur(20px);
}
.hero-value {
    font-size: clamp(2.1rem, 1.7rem + 1.5vw, 3.2rem);
    font-weight: 900;
    line-height: 1;
    letter-spacing: -0.05em;
}
.hero-meta {
    color: var(--muted);
    margin-top: .45rem;
    font-size: .92rem;
}
.avg-hint {
    color: var(--muted);
    font-size: .85rem;
    margin-top: -.25rem;
    margin-bottom: .75rem;
}
.mini-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: .8rem;
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
    background: linear-gradient(135deg, #ffb199, #FF3B30);
    color: white;
}
.avatar-fallback {
    width: 54px;
    height: 54px;
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    color: white;
}
.avatar-h { background: linear-gradient(135deg, #FF3B30, #ff7a73); }
.avatar-d { background: linear-gradient(135deg, #34C759, #5ee38c); }
.avatar-input {
    width: 74px;
    height: 74px;
    border-radius: 999px;
    object-fit: cover;
    border: 2px solid rgba(255,255,255,0.12);
    box-shadow: 0 10px 24px rgba(0,0,0,0.18);
}
.empty-state {
    text-align: center;
}
.empty-icon {
    font-size: 2rem;
    margin-bottom: .35rem;
}
.success-chip {
    display: inline-block;
    padding: .3rem .65rem;
    border-radius: 999px;
    background: rgba(52,199,89,0.16);
    border: 1px solid rgba(52,199,89,0.28);
    color: #bff3cc;
    font-size: .82rem;
    font-weight: 700;
}
[data-testid="stMetric"] {
    background: linear-gradient(180deg, rgba(255,255,255,0.09), rgba(255,255,255,0.04));
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 20px;
    padding: .9rem 1rem;
    box-shadow: 0 10px 25px rgba(0,0,0,0.16);
}
[data-testid="stMetricLabel"] { color: var(--muted); }
[data-testid="stMetricValue"] { font-weight: 850; letter-spacing: -0.04em; }
.stButton > button, .stDownloadButton > button {
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.10);
    background: linear-gradient(180deg, rgba(255,255,255,0.11), rgba(255,255,255,0.06));
    color: white;
    min-height: 3rem;
    font-weight: 800;
    transition: all .18s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-1px);
    border-color: rgba(255,255,255,0.16);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(255,59,48,0.96), rgba(255,59,48,0.78));
    box-shadow: 0 12px 28px rgba(255,59,48,0.25);
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, rgba(255,59,48,1), rgba(255,107,99,0.88));
}
.stDownloadButton > button {
    background: linear-gradient(135deg, rgba(52,199,89,0.22), rgba(52,199,89,0.14));
    border: 1px solid rgba(52,199,89,0.24);
}
.stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] > div, textarea {
    border-radius: 18px !important;
    background: rgba(255,255,255,0.07) !important;
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
    st.markdown('<div style="max-width:760px;margin:0 auto 1rem auto;">', unsafe_allow_html=True)
    st.image(str(HEADER), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

pages = [
    st.Page("pages/1_eingabe.py", title="Eingabe", icon="✍️", default=True),
    st.Page("pages/2_statistiken.py", title="Statistiken", icon="📊"),
    st.Page("pages/3_rekorde.py", title="Rekorde", icon="🏆"),
]
st.navigation(pages, position="top").run()
