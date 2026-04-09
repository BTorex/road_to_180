
from datetime import date
import streamlit as st
from services import PLAYERS, delete_average, fetch_averages, insert_average, player_image, safe_toast, update_average

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
st.markdown('<div class="page-subtitle">Schneller Mobile-First Flow für neue Einträge und saubere Historienbearbeitung.</div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Schnelleingabe</div>', unsafe_allow_html=True)

player = st.segmented_control("Spieler", PLAYERS, default="Hanno")
play_date = st.date_input("Datum", value=date.today())
average = st.number_input("Average (3er Schnitt)", min_value=0.0, max_value=180.0, step=0.1, format="%.1f")
comment = st.text_input("Kommentar", placeholder="z. B. Training, Liga, starker Start …")

if st.button("➕ Eintrag speichern", use_container_width=True, type="primary", disabled=average <= 0):
    try:
        insert_average(play_date=play_date, player=player, average=average, comment=comment)
        safe_toast(f"{player} mit {average:.1f} gespeichert", "🎯")
        st.rerun()
    except Exception as exc:
        st.error(f"Fehler beim Speichern: {exc}")

history_df = fetch_averages(limit=30, order_desc=True)
st.markdown('<div class="section-label">Historie</div>', unsafe_allow_html=True)

if history_df.empty:
    st.info("Noch keine Einträge vorhanden.")
else:
    for _, row in history_df.iterrows():
        player_name = row["player"]
        label = f"ID {int(row['id'])} · {row['play_date'].strftime('%d.%m.%Y')} · {player_name} · {float(row['average']):.1f}"
        with st.expander(label, expanded=False):
            meta1, meta2 = st.columns([0.2, 0.8])
            with meta1:
                img = player_image(player_name)
                if img:
                    st.image(img, width=56)
            with meta2:
                st.markdown(f"**{player_name}**")
                st.caption(row['play_date'].strftime('%d.%m.%Y'))
                if row.get('comment'):
                    st.write(row['comment'])

            new_avg = st.number_input(
                f"Average aktualisieren #{int(row['id'])}",
                min_value=0.0,
                max_value=180.0,
                value=float(row['average']),
                step=0.1,
                format="%.1f",
                key=f"avg_{int(row['id'])}",
            )
            new_comment = st.text_input(
                f"Kommentar #{int(row['id'])}",
                value=row['comment'] if row['comment'] else "",
                key=f"comment_{int(row['id'])}",
            )
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
