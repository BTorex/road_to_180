import streamlit as st
import pandas as pd
from supabase import create_client

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

st.write("### 🏆 All-Time Highs")
st.markdown("<div style='color: #888; font-size: 0.85rem; margin-bottom: 15px;'>Die ewigen Rekorde. Wer hält die Krone?</div>", unsafe_allow_html=True)

response = supabase.table("dart_averages").select("*").execute()

if not response.data:
    st.info("Noch keine Rekorde vorhanden.")
    st.stop()

df = pd.DataFrame(response.data)
df['play_date'] = pd.to_datetime(df['play_date']).dt.strftime('%d.%m.%Y')
if 'comment' not in df.columns: df['comment'] = ""

# Symbole im Tab durch Buchstaben ersetzt
tab_all, tab1, tab2 = st.tabs(["🌍 Gesamtes Ranking", "🔵 H", "🟠 D"])

def draw_leaderboard(dataframe, limit=5, show_avatar=False):
    top_df = dataframe.nlargest(limit, 'average')
    for i, row in enumerate(top_df.itertuples(), 1):
        medal = "👑" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🎯"
        color = "#007AFF" if row.player == "Hanno" else "#FF9500"
        
        comment_html = ""
        if pd.notna(row.comment) and str(row.comment).strip() != "":
            comment_html = f"<div style='margin-top: 8px; font-size: 0.9rem; color: #888; font-style: italic;'>💬 {row.comment}</div>"
            
        player_tag = f"<span style='background: {color}20; color: {color}; padding: 2px 8px; border-radius: 10px; font-size: 0.8rem; margin-left: 10px;'>{row.player}</span>" if show_avatar else ""

        st.markdown(f"""
        <div style="background: rgba(150, 150, 150, 0.05); padding: 18px; border-radius: 16px; margin-bottom: 12px; border: 1px solid rgba(150,150,150,0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 700; font-size: 1.1rem;">{i}. Platz {medal} {player_tag}</span>
                <span style="font-weight: 800; font-size: 1.4rem; color: {color};">{row.average:.2f}</span>
            </div>
            <div style="color: #666; font-size: 0.85rem; margin-top: 4px; font-weight: 500;">📅 Gespielt am {row.play_date}</div>
            {comment_html}
        </div>
        """, unsafe_allow_html=True)

with tab_all:
    st.write("#### 🌍 Top 10 Overall")
    draw_leaderboard(df, limit=10, show_avatar=True)

with tab1:
    st.markdown("<div class='avatar-container'><div class='avatar avatar-h'>H</div></div>", unsafe_allow_html=True)
    draw_leaderboard(df[df['player'] == "Hanno"], limit=5)

with tab2:
    st.markdown("<div class='avatar-container'><div class='avatar avatar-d'>D</div></div>", unsafe_allow_html=True)
    draw_leaderboard(df[df['player'] == "Dominik"], limit=5)
