import streamlit as st
import pandas as pd
from supabase import create_client

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

st.write("### 🏆 All-Time Highs (Top 5)")

response = supabase.table("dart_averages").select("*").execute()

if not response.data:
    st.info("Noch keine Rekorde vorhanden.")
    st.stop()

df = pd.DataFrame(response.data)
df['play_date'] = pd.to_datetime(df['play_date']).dt.strftime('%d.%m.%Y')

# Sicherstellen, dass die Kommentarspalte existiert
if 'comment' not in df.columns:
    df['comment'] = ""

tab1, tab2 = st.tabs(["🎯 Hanno", "🎯 Dominik"])

for tab, player, avatar_class, letter in zip([tab1, tab2], ["Hanno", "Dominik"], ["avatar-h", "avatar-d"], ["H", "D"]):
    with tab:
        # Avatar zentriert anzeigen
        st.markdown(f"<div class='avatar-container'><div class='avatar {avatar_class}'>{letter}</div></div>", unsafe_allow_html=True)
        
        player_df = df[df['player'] == player].nlargest(5, 'average')
        
        if not player_df.empty:
            for i, row in enumerate(player_df.itertuples(), 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🎯"
                
                # Kommentar formattieren, falls vorhanden
                comment_html = ""
                if pd.notna(row.comment) and str(row.comment).strip() != "":
                    comment_html = f"<div style='margin-top: 8px; font-size: 0.9rem; color: #888; font-style: italic;'>💬 {row.comment}</div>"
                
                # Elegante Karte rendern
                color = "#007AFF" if player == "Hanno" else "#FF9500"
                st.markdown(f"""
                <div style="background: rgba(150, 150, 150, 0.05); padding: 18px; border-radius: 16px; margin-bottom: 12px; border: 1px solid rgba(150,150,150,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; font-size: 1.1rem;">{i}. Platz {medal}</span>
                        <span style="font-weight: 800; font-size: 1.4rem; color: {color};">{row.average:.2f}</span>
                    </div>
                    <div style="color: #666; font-size: 0.85rem; margin-top: 4px; font-weight: 500;">📅 Gespielt am {row.play_date}</div>
                    {comment_html}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("Noch keine Spiele eingetragen.")
