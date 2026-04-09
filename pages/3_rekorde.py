import pandas as pd
import streamlit as st
from supabase import create_client, Client

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
    df["average"] = pd.to_numeric(df["average"])
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


st.markdown('<div class="page-title">All-Time Highs</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Top 10 overall und die besten fünf Averages je Spieler.</div>', unsafe_allow_html=True)

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
    hanno = df[df["player"] == "Hanno"].head(5).reset_index(drop=True)
    for idx, row in hanno.iterrows():
        render_record_card(idx + 1, row)

with dominik_tab:
    dominik = df[df["player"] == "Dominik"].head(5).reset_index(drop=True)
    for idx, row in dominik.iterrows():
        render_record_card(idx + 1, row)
