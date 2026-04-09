from datetime import date
from urllib.parse import quote
import streamlit as st
from services import PLAYERS, delete_average, fetch_averages, format_date_de, format_time_de, insert_average, player_image, safe_toast, update_average

if "confirm_delete_id" not in st.session_state:
    st.session_state.confirm_delete_id = None

@st.dialog("Löschen bestätigen")
def confirm_delete_dialog(row_id: int, label: str):
    st.markdown(f"Möchtest du den Eintrag wirklich löschen?\n\n**{label}**")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Ja, löschen", use_container_width=True, type="primary"):
            try:
                delete_average(row_id)
                st.session_state.confirm_delete_id = None
                safe_toast("Eintrag gelöscht", "🗑️")
                st.rerun()
            except Exception as exc:
                st.error(f"Fehler beim Löschen: {exc}")
    with c2:
        if st.button("Abbrechen", use_container_width=True):
            st.session_state.confirm_delete_id = None
            st.rerun()

st.markdown('<div class="page-title">Averages erfassen</div>', unsafe_allow_html=True)
st.markdown('<div class="input-shell">', unsafe_allow_html=True)
player = st.segmented_control("Spieler", PLAYERS, default="Hanno")
play_date = st.date_input("Datum", value=date.today())
avg_col, info_col = st.columns([1.15, 0.85])
with avg_col:
    average = st.number_input("Average", min_value=0.0, max_value=180.0, step=0.1, format="%.1f")
    st.markdown('<div class="avg-hint">Saubere Eingabe für den 3-Dart-Average mit einer Nachkommastelle.</div>', unsafe_allow_html=True)
with info_col:
    hero_html = f"<div class='hero-kpi'><div class='kicker'>Sofort-Check</div><div class='hero-value'>{average:.1f}</div><div class='hero-meta'>{player} · {play_date.strftime('%d.%m.%Y')}</div></div>"
    st.markdown(hero_html, unsafe_allow_html=True)
comment = st.text_input("Kommentar", placeholder="z. B. Training, Liga, starker Start …")
st.markdown('</div>', unsafe_allow_html=True)

save1, save2 = st.columns([1,1])
with save1:
    if st.button("➕ Eintrag speichern", use_container_width=True, type="primary", disabled=average <= 0):
        try:
            insert_average(play_date=play_date, player=player, average=average, comment=comment)
            safe_toast(f"{player} mit {average:.1f} gespeichert", "🎯")
            st.rerun()
        except Exception as exc:
            st.error(f"Fehler beim Speichern: {exc}")

history_df = fetch_averages(limit=50, order_desc=True)
with save2:
    if not history_df.empty:
        mail_subject = quote("Road to 180 – Export Eingabe")
        mail_body = quote(f"Einträge: {len(history_df)}")
        st.link_button("Per E-Mail teilen", f"mailto:?subject={mail_subject}&body={mail_body}", use_container_width=True)

if not history_df.empty:
    csv_df = history_df.copy()
    csv_df["play_date"] = csv_df["play_date"].dt.strftime("%d.%m.%Y")
    csv_df["created_at"] = csv_df["created_at"].dt.strftime("%d.%m.%Y %H:%M")
    st.download_button("CSV exportieren", data=csv_df.to_csv(index=False, sep=";", encoding="utf-8-sig").encode("utf-8-sig"), file_name="road_to_180_eingabe_export.csv", mime="text/csv", use_container_width=True)

if history_df.empty:
    st.info("Noch keine Einträge vorhanden.")
else:
    st.markdown('<div class="section-label">Historie</div>', unsafe_allow_html=True)
    for _, row in history_df.iterrows():
        player_name = row["player"]
        label = f"{format_date_de(row['play_date'])} · {player_name} · {float(row['average']):.1f}"
        with st.expander(label, expanded=False):
            meta1, meta2 = st.columns([0.2, 0.8])
            with meta1:
                img = player_image(player_name)
                if img:
                    st.image(img, width=56)
            with meta2:
                st.markdown(f"**{player_name}**")
                st.caption(f"Spieltag: {format_date_de(row['play_date'])} · Erfasst: {format_time_de(row['created_at'])} Uhr")
                if row.get('comment') and str(row.get('comment')).lower() != 'nan':
                    st.write(row['comment'])
            new_avg = st.number_input(f"Average aktualisieren #{int(row['id'])}", min_value=0.0, max_value=180.0, value=float(row['average']), step=0.1, format="%.1f", key=f"avg_{int(row['id'])}")
            new_comment = st.text_input(f"Kommentar #{int(row['id'])}", value="" if not row['comment'] or str(row['comment']).lower() == 'nan' else row['comment'], key=f"comment_{int(row['id'])}")
            b1, b2 = st.columns(2)
            with b1:
                if st.button("💾 Speichern", use_container_width=True, key=f"save_{int(row['id'])}"):
                    try:
                        update_average(int(row['id']), new_avg, new_comment)
                        safe_toast("Eintrag aktualisiert", "✅")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Fehler beim Update: {exc}")
            with b2:
                if st.button("🗑️ Löschen", use_container_width=True, key=f"delete_{int(row['id'])}"):
                    st.session_state.confirm_delete_id = int(row['id'])
        if st.session_state.confirm_delete_id == int(row['id']):
            confirm_delete_dialog(int(row['id']), label)
