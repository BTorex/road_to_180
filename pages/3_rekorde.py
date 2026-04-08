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
# Deutsches Datum formatieren
df['play_date'] = pd.to_datetime(df['play_date']).dt.strftime('%d.%m.%Y')

tab1, tab2 = st.tabs(["🎯 Hanno", "🎯 Dominik"])

for tab, player in zip([tab1, tab2], ["Hanno", "Dominik"]):
    with tab:
        # Filtern, nach Average sortieren und die Top 5 nehmen
        player_df = df[df['player'] == player].nlargest(5, 'average')
        
        if not player_df.empty:
            # Schön formatierte Ausgabe
            for i, row in enumerate(player_df.itertuples(), 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🎯"
                st.write(f"**{i}. Platz {medal}**")
                st.metric(label=f"Gespielt am {row.play_date}", value=f"{row.average:.2f}")
                st.write("") # Spacer
        else:
            st.write("Noch keine Spiele eingetragen.")
