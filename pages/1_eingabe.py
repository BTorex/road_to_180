import streamlit as st
import pandas as pd
from supabase import create_client

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# --- HAUPT-TABS ---
main_tab1, main_tab2 = st.tabs(["📝 Neu eintragen", "⚙️ Historie bearbeiten"])

# ==========================================
# TAB 1: NEU EINTRAGEN
# ==========================================
with main_tab1:
    selected_date = st.date_input("Spieldatum", format="DD.MM.YYYY", label_visibility="collapsed")
    
    p_tab1, p_tab2 = st.tabs(["Hanno", "Dominik"])
    
    with p_tab1:
        st.markdown("<div class='avatar-container'><div class='avatar avatar-h'>H</div></div>", unsafe_allow_html=True)
        hanno_avg = st.number_input("Schnitt (Hanno)", min_value=0.0, max_value=180.0, step=0.1, key="h_avg_new")
        hanno_comment = st.text_input("Kommentar / Besonderheit (optional)", placeholder="z.B. 170er Finish verpasst...", key="h_comm_new")
        
        if st.button("Speichern für Hanno", use_container_width=True, type="primary"):
            supabase.table("dart_averages").insert({
                "play_date": str(selected_date), "player": "Hanno", "average": hanno_avg, "comment": hanno_comment
            }).execute()
            st.success("Eintrag gespeichert! 🎯")

    with p_tab2:
        st.markdown("<div class='avatar-container'><div class='avatar avatar-d'>D</div></div>", unsafe_allow_html=True)
        dominik_avg = st.number_input("Schnitt (Dominik)", min_value=0.0, max_value=180.0, step=0.1, key="d_avg_new")
        dominik_comment = st.text_input("Kommentar / Besonderheit (optional)", placeholder="z.B. Neues Setup probiert...", key="d_comm_new")
        
        if st.button("Speichern für Dominik", use_container_width=True, type="primary"):
            supabase.table("dart_averages").insert({
                "play_date": str(selected_date), "player": "Dominik", "average": dominik_avg, "comment": dominik_comment
            }).execute()
            st.success("Eintrag gespeichert! 🎯")

# ==========================================
# TAB 2: BEARBEITEN / KORRIGIEREN
# ==========================================
with main_tab2:
    st.write("### Eintrag anpassen")
    
    # Letzte 30 Einträge laden
    response = supabase.table("dart_averages").select("*").order("id", desc=True).limit(30).execute()
    
    if response.data:
        df = pd.DataFrame(response.data)
        df['play_date'] = pd.to_datetime(df['play_date']).dt.strftime('%d.%m.%Y')
        
        # Dropdown für die Auswahl generieren
        options = []
        for _, row in df.iterrows():
            kommentar_str = f" | 💬 {row.get('comment', '')}" if pd.notna(row.get('comment')) and row.get('comment') else ""
            display_text = f"{row['play_date']} - {row['player']}: {row['average']:.1f}{kommentar_str}"
            options.append((row['id'], display_text, row['average'], row.get('comment', '')))
            
        selected_entry = st.selectbox("Wähle das Spiel aus:", options, format_func=lambda x: x[1])
        
        if selected_entry:
            edit_id, _, edit_avg, edit_comment = selected_entry
            
            with st.container(border=True):
                st.write("Werte aktualisieren:")
                new_avg = st.number_input("Neuer Schnitt", value=float(edit_avg), min_value=0.0, step=0.1)
                new_comment = st.text_input("Kommentar", value=edit_comment if edit_comment else "")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("💾 Update", use_container_width=True, type="primary"):
                        supabase.table("dart_averages").update({"average": new_avg, "comment": new_comment}).eq("id", edit_id).execute()
                        st.success("Erfolgreich aktualisiert! (Lade Seite neu)")
                with col_b:
                    if st.button("🗑️ Löschen", use_container_width=True):
                        supabase.table("dart_averages").delete().eq("id", edit_id).execute()
                        st.error("Eintrag gelöscht! (Lade Seite neu)")

st.divider()

# --- LETZTE EINTRÄGE ANZEIGEN ---
st.write("### 📊 Letzte Aktivitäten")
response_recent = supabase.table("dart_averages").select("*").order("id", desc=True).limit(8).execute()

if response_recent.data:
    df_recent = pd.DataFrame(response_recent.data)
    df_recent['Datum'] = pd.to_datetime(df_recent['play_date']).dt.strftime('%d.%m.')
    # Kommentarspalte sicherstellen
    if 'comment' not in df_recent.columns:
        df_recent['comment'] = ""
    df_recent['Kommentar'] = df_recent['comment'].fillna("")
    
    df_display = df_recent.rename(columns={"player": "Wer", "average": "Schnitt"})
    st.dataframe(df_display[["Datum", "Wer", "Schnitt", "Kommentar"]], use_container_width=True, hide_index=True)
