
import html
import base64
from pathlib import Path
import streamlit as st
from services import fetch_averages, format_date_de, player_image

def img_to_data_uri(path_str: str) -> str:
    path = Path(path_str)
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"

def avatar_html(player: str) -> str:
    image_path = player_image(player)
    if image_path:
        return f"<img src='{img_to_data_uri(image_path)}' style='width:46px;height:46px;border-radius:999px;object-fit:cover;border:2px solid rgba(255,255,255,0.14);' />"
    css_class = "avatar-h" if player == "Hanno" else "avatar-d"
    return f"<div class='avatar-fallback {css_class}'>{html.escape(player[:1])}</div>"

def clean_comment(value) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return "" if text.lower() == 'nan' else text

def record_card(rank: int, row):
    player = html.escape(str(row["player"]))
    rank_class = "rank-chip rank-top" if rank <= 3 else "rank-chip"
    comment = clean_comment(row.get("comment"))
    comment_html = f"<div class='small-muted' style='margin-top:0.35rem;'>{html.escape(comment)}</div>" if comment else ""
    card = f"""
    <div class="record-card">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:0.9rem;">
            <div style="display:flex;align-items:center;gap:0.9rem;">
                <div class="{rank_class}">{rank}</div>
                <div>
                    <div style="font-size:1.3rem;font-weight:800;letter-spacing:-0.03em;">{float(row['average']):.1f}</div>
                    <div class="small-muted">{player} · {format_date_de(row['play_date'])}</div>
                    {comment_html}
                </div>
            </div>
            {avatar_html(str(row['player']))}
        </div>
    </div>
    """
    st.markdown(card, unsafe_allow_html=True)

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
    st.markdown(f"<div class='small-muted'>All-Time High: <span style='font-weight:800;color:{color};'>{top:.1f}</span> · Ø: <span style='font-weight:800;color:{color};'>{mean:.1f}</span> · Median: <span style='font-weight:800;color:{color};'>{median:.1f}</span> · Spiele: <span style='font-weight:800;'>{count}</span></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="page-title">Rekorde</div>', unsafe_allow_html=True)

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
    player_summary("Hanno", df, "#5aa8ff")
    for idx, row in df[df["player"] == "Hanno"].head(5).iterrows():
        record_card(idx + 1, row)

with dominik_tab:
    player_summary("Dominik", df, "#ffab66")
    for idx, row in df[df["player"] == "Dominik"].head(5).iterrows():
        record_card(idx + 1, row)
