import pandas as pd
import streamlit as st
from supabase import Client, create_client

@st.cache_resource
def init_connection() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()


def load_data() -> pd.DataFrame:
    response = (
        supabase.table("dart_averages")
        .select("id, play_date, player, average, comment")
        .order("average", desc=True)
        .execute()
    )
    df = pd.DataFrame(response.data or [])
    if df.empty:
        return df
    df["play_date"] = pd.to_datetime(df["play_date"])
    df["average"] = pd.to_numeric(df["average"], errors="coerce")
    df = df.dropna(subset=["average"])
    return df


def render_record_card(rank: int, row: pd.Series):
    player = row["player"]
    avatar_class = "avatar-h" if player == "Hanno" else "avatar-d"
    initial = player[0]
    rank_class = "rank-chip rank-top" if rank <= 3 else "rank-chip"
    comment = row.get("comment") if pd.notna(row.get("comment")) else ""
    comment_html = f'<div class="small-muted" style="margin-top:0.35rem;">{comment}</div>' if comment else ""
    html = f"""
    <div class="record-card">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:0.9rem;">
            <div style="display:flex;align-items:center;gap:0.9rem;">
                <div class="{rank_class}">{rank}</div>
                <div>
                    <div style="font-size:1.3rem;font-weight:800;letter-spacing:-0.03em;">{float(row['average']):.1f}</div>
                    <div class="small-muted">{player} · {row['play_date'].strftime('%d.%m.%Y')}</div>
                    {comment_html}
                </div>
            </div>
            <div class="avatar {avatar_class}">{initial}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_summary(player: str, df: pd.DataFrame, color: str):
    p = df[df["player"] == player]
    if p.empty:
        st.info(f"Keine Daten für {player} vorhanden.")
        return
    top = p.iloc[0]["average"]
    mean = p["average"].mean()
    count = len(p)
    st.markdown('<div class="hero-panel">', unsafe_allow_html=True)
    st.markdown(f"**{player}**")
    st.markdown(f"<div class='small-muted'>Alltime High: <span style='color:{color};font-weight:800;'>{top:.1f}</span> · Ø Gesamt: <span style='color:{color};font-weight:800;'>{mean:.1f}</span> · Spiele: <span style='font-weight:800;'>{count}</span></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


st.markdown('<div class="page-title">All-Time Highs</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Top 10 overall und individuelle Top-5-Ansichten inklusive Kommentare.</div>', unsafe_allow_html=True)

df = load_data()
if df.empty:
    st.info("Noch keine Daten vorhanden.")
    st.stop()

overall_tab, hanno_tab, dominik_tab = st.tabs(["Overall Top 10", "Hanno Top 5", "Dominik Top 5"])

with overall_tab:
    top10 = df.head(10).reset_index(drop=True)
    for idx, row in top10.iterrows():
        render_record_card(idx + 1, row)

with hanno_tab:
    render_summary("Hanno", df, "#4da3ff")
    hanno = df[df["player"] == "Hanno"].head(5).reset_index(drop=True)
    for idx, row in hanno.iterrows():
        render_record_card(idx + 1, row)

with dominik_tab:
    render_summary("Dominik", df, "#ff9d4d")
    dominik = df[df["player"] == "Dominik"].head(5).reset_index(drop=True)
    for idx, row in dominik.iterrows():
        render_record_card(idx + 1, row)
