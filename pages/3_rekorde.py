
import html
import streamlit as st
from services import fetch_averages, format_date_de, player_image

def clean_comment(value) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return "" if text.lower() == 'nan' else text

def record_card(rank: int, row):
    player = str(row["player"])
    rank_class = "rank-chip rank-top" if rank <= 3 else "rank-chip"
    comment = clean_comment(row.get("comment"))
    st.markdown('<div class="record-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([0.12, 0.68, 0.20])
    with c1:
        st.markdown(f'<div class="{rank_class}">{rank}</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div style='font-size:1.3rem;font-weight:800;letter-spacing:-0.03em;'>{float(row['average']):.1f}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='small-muted'>{html.escape(player)} · {format_date_de(row['play_date'])}</div>", unsafe_allow_html=True)
        if comment:
            st.markdown(f"<div class='small-muted' style='margin-top:.35rem;'>{html.escape(comment)}</div>", unsafe_allow_html=True)
    with c3:
        img = player_image(player)
        if img:
            st.image(img, width=46)
        else:
            css_class = "avatar-h" if player == "Hanno" else "avatar-d"
            st.markdown(f'<div class="avatar-fallback {css_class}">{html.escape(player[:1])}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def player_summary(player: str, df, color: str):
    pdf = df[df["player"] == player]
    if pdf.empty:
        st.info(f"Keine Daten für {player} vorhanden.")
        return
    top = pdf.iloc[0]["average"]
    mean = pdf["average"].mean()
    median = pdf["average"].median()
    count = len(pdf)
    st.markdown('<div class="hero-panel">', unsafe_allow_html=True)
    st.markdown(f"**{player}**")
    st.markdown(f"<div class='small-muted'>High: <span style='font-weight:800;color:{color};'>{top:.1f}</span> · Ø: <span style='font-weight:800;color:{color};'>{mean:.1f}</span> · Median: <span style='font-weight:800;color:{color};'>{median:.1f}</span> · Spiele: <span style='font-weight:800;'>{count}</span></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="page-title">Rekorde</div>', unsafe_allow_html=True)
st.markdown('<div class="small-muted" style="margin-bottom:.7rem;">Kurz erklärt: Hier siehst du eure stärksten Einzelwerte und schnellen Bestmarken auf einen Blick.</div>', unsafe_allow_html=True)

df = fetch_averages()
if df.empty:
    st.info("Noch keine Daten vorhanden.")
    st.stop()

df = df.sort_values(["average", "play_date", "id"], ascending=[False, False, False]).reset_index(drop=True)
overall_tab, hanno_tab, dominik_tab = st.tabs(["Overall Top 10", "Hanno Top 5", "Dominik Top 5"])

with overall_tab:
    for idx, row in df.head(10).iterrows():
        record_card(idx + 1, row)
with hanno_tab:
    player_summary("Hanno", df, "#FF3B30")
    for idx, row in df[df["player"] == "Hanno"].head(5).iterrows():
        record_card(idx + 1, row)
with dominik_tab:
    player_summary("Dominik", df, "#34C759")
    for idx, row in df[df["player"] == "Dominik"].head(5).iterrows():
        record_card(idx + 1, row)
