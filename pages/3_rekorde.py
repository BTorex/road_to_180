import pandas as pd
import streamlit as st

from services import add_checkout_metrics, fetch_averages


def render_record_card(rank: int, row: pd.Series):
    player = row["player"]
    avatar_class = "avatar-h" if player == "Hanno" else "avatar-d"
    initial = player[0]
    rank_class = "rank-chip rank-top" if rank <= 3 else "rank-chip"
    comment = row.get("comment") if pd.notna(row.get("comment")) else ""
    checkout = row.get("checkout_rate")
    checkout_html = f'<div class="small-muted">Checkout: {float(checkout):.1f}%</div>' if pd.notna(checkout) else ''
    comment_html = f'<div class="small-muted" style="margin-top:0.35rem;">{comment}</div>' if comment else ''
    html = f"""
    <div class="record-card">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:0.9rem;">
            <div style="display:flex;align-items:center;gap:0.9rem;">
                <div class="{rank_class}">{rank}</div>
                <div>
                    <div style="font-size:1.3rem;font-weight:800;letter-spacing:-0.03em;">{float(row['average']):.1f}</div>
                    <div class="small-muted">{player} · {row['play_date'].strftime('%d.%m.%Y')}</div>
                    {checkout_html}
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
    checkout = p["checkout_rate"].dropna().mean() if "checkout_rate" in p.columns else None
    checkout_text = f" · Ø Checkout: <span style='font-weight:800;color:{color};'>{checkout:.1f}%</span>" if checkout is not None else ""
    st.markdown('<div class="hero-panel">', unsafe_allow_html=True)
    st.markdown(f"**{player}**")
    st.markdown(f"<div class='small-muted'>Alltime High: <span style='color:{color};font-weight:800;'>{top:.1f}</span> · Ø Gesamt: <span style='color:{color};font-weight:800;'>{mean:.1f}</span> · Spiele: <span style='font-weight:800;'>{count}</span>{checkout_text}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


st.markdown('<div class="page-title">All-Time Highs</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Rekorde mit Kommentaren und optionaler Doppelquote pro Eintrag.</div>', unsafe_allow_html=True)

df = add_checkout_metrics(fetch_averages())
if df.empty:
    st.info("Noch keine Daten vorhanden.")
    st.stop()

df = df.sort_values(["average", "play_date", "id"], ascending=[False, False, False])

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
