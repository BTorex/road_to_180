from datetime import date

import pandas as pd
import streamlit as st

from services import (
    PLAYERS,
    add_checkout_metrics,
    delete_average,
    fetch_averages,
    insert_average,
    safe_toast,
    update_average,
)

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


st.markdown('<div class="page-title">Neue Averages erfassen</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Mobile-first Eingabe mit optionalem Checkout-Tracking und Inline-Edit per Expander.</div>',
    unsafe_allow_html=True,
)

with st.container():
    st.markdown('<div class="section-label">Schnelleingabe</div>', unsafe_allow_html=True)

    left, right = st.columns([1, 1])

    with left:
        player = st.segmented_control("Spieler", PLAYERS, default="Hanno")
        play_date = st.date_input("Datum", value=date.today())
        average = st.number_input(
            "Average (3er Schnitt)",
            min_value=0.0,
            max_value=180.0,
            step=0.1,
            format="%.1f",
        )

    with right:
        comment = st.text_input("Kommentar", placeholder="z. B. Liga, Training, Warm-up …")
        st.markdown(
            '<div class="section-label" style="margin-top:0.4rem;">Checkout-Tracking</div>',
            unsafe_allow_html=True,
        )
        darts_on_double = st.number_input("Darts auf Doppel", min_value=0, step=1, value=0)
        hits_on_double = st.number_input("Getroffene Doppel", min_value=0, step=1, value=0)

    invalid_checkout = hits_on_double > darts_on_double if darts_on_double >= 0 else False
    if invalid_checkout:
        st.warning("Getroffene Doppel dürfen nicht größer als Darts auf Doppel sein.")

    save_disabled = average <= 0 or invalid_checkout

    if st.button("➕ Eintrag speichern", use_container_width=True, type="primary", disabled=save_disabled):
        try:
            insert_average(
                play_date=play_date,
                player=player,
                average=average,
                comment=comment,
                darts_on_double=darts_on_double if darts_on_double > 0 else None,
                hits_on_double=hits_on_double if darts_on_double > 0 else None,
            )
            safe_toast(f"{player} mit {average:.1f} gespeichert", "🎯")
            st.rerun()
        except Exception as exc:
            st.error(f"Fehler beim Speichern: {exc}")

history_df = add_checkout_metrics(fetch_averages(limit=30, order_desc=True))

st.markdown('<div class="section-label">Historie</div>', unsafe_allow_html=True)

if history_df.empty:
    st.info("Noch keine Einträge vorhanden.")
else:
    for _, row in history_df.iterrows():
        player_name = row["player"]
        label = (
            f"ID {int(row['id'])} · "
            f"{row['play_date'].strftime('%d.%m.%Y')} · "
            f"{player_name} · "
            f"{float(row['average']):.1f}"
        )

        with st.expander(label, expanded=False):
            c1, c2, c3 = st.columns([1, 1, 1])

            with c1:
                st.metric("Average", f"{float(row['average']):.1f}")

            with c2:
                if pd.notna(row.get("checkout_rate")):
                    st.metric("Checkout %", f"{float(row['checkout_rate']):.1f}%")
                else:
                    st.metric("Checkout %", "—")

            with c3:
                st.metric("Spieler", player_name)

            e1, e2 = st.columns([1, 1])

            with e1:
                new_avg = st.number_input(
                    f"Average aktualisieren #{int(row['id'])}",
                    min_value=0.0,
                    max_value=180.0,
                    value=float(row["average"]),
                    step=0.1,
                    format="%.1f",
                    key=f"avg_{int(row['id'])}",
                )
                new_comment = st.text_input(
                    f"Kommentar #{int(row['id'])}",
                    value=row["comment"] if pd.notna(row["comment"]) else "",
                    key=f"comment_{int(row['id'])}",
                )

            with e2:
                new_darts = st.number_input(
                    f"Darts auf Doppel #{int(row['id'])}",
                    min_value=0,
                    step=1,
                    value=int(row["darts_on_double"]) if pd.notna(row["darts_on_double"]) else 0,
                    key=f"dod_{int(row['id'])}",
                )
                new_hits = st.number_input(
                    f"Getroffene Doppel #{int(row['id'])}",
                    min_value=0,
                    step=1,
                    value=int(row["hits_on_double"]) if pd.notna(row["hits_on_double"]) else 0,
                    key=f"hod_{int(row['id'])}",
                )

            if new_hits > new_darts:
                st.warning("Getroffene Doppel dürfen nicht größer als Darts auf Doppel sein.")

            b1, b2 = st.columns(2)

            with b1:
                if st.button(
                    "💾 Speichern",
                    use_container_width=True,
                    key=f"save_{int(row['id'])}",
                    disabled=new_hits > new_darts,
                ):
                    try:
                        update_average(
                            int(row["id"]),
                            new_avg,
                            new_comment,
                            darts_on_double=new_darts if new_darts > 0 else None,
                            hits_on_double=new_hits if new_darts > 0 else None,
                        )
                        safe_toast("Eintrag aktualisiert", "✅")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Fehler beim Update: {exc}")

            with b2:
                if st.button("🗑️ Löschen", use_container_width=True, key=f"delete_{int(row['id'])}"):
                    st.session_state.confirm_delete_id = int(row["id"])

        if st.session_state.confirm_delete_id == int(row["id"]):
            confirm_delete_dialog(int(row["id"]), label)
