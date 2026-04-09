from datetime import date
import pandas as pd
import streamlit as st
from supabase import Client, create_client

PLAYERS = ["Hanno", "Dominik"]

@st.cache_resource
def init_connection() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

if "selected_edit_id" not in st.session_state:
    st.session_state.selected_edit_id = None
if "confirm_delete_id" not in st.session_state:
    st.session_state.confirm_delete_id = None


def safe_toast(msg: str, icon: str | None = None):
    try:
        st.toast(msg, icon=icon)
    except Exception:
        st.success(msg)


def load_history(limit: int = 30) -> pd.DataFrame:
    response = (
        supabase.table("dart_averages")
        .select("id, play_date, player, average, comment, created_at")
        .order("id", desc=True)
        .limit(limit)
        .execute()
    )
    df = pd.DataFrame(response.data or [])
    if df.empty:
        return df
    df["play_date"] = pd.to_datetime(df["play_date"])
    df["average"] = pd.to_numeric(df["average"], errors="coerce")
    return df


def insert_average(play_date: date, player: str, average: float, comment: str | None):
    payload = {
        "play_date": str(play_date),
        "player": player,
        "average": float(average),
        "comment": comment or None,
    }
    return supabase.table("dart_averages").insert(payload).execute()


def update_average(row_id: int, average: float, comment: str | None):
    payload = {"average": float(average), "comment": comment or None}
    return supabase.table("dart_averages").update(payload).eq("id", row_id).execute()


def delete_average(row_id: int):
    return supabase.table("dart_averages").delete().eq("id", row_id).execute()


@st.dialog("Löschen bestätigen")
def confirm_delete_dialog(row_id: int, label: str):
    st.write(f"Möchtest du den Eintrag wirklich löschen?

**{label}**")
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
st.markdown('<div class="page-subtitle">Robuste CRUD-Seite mit schnellem Mobile-Flow, History-Edit und Delete-Confirm.</div>', unsafe_allow_html=True)

new_tab, edit_tab = st.tabs(["Neu eintragen", "Historie bearbeiten"])

with new_tab:
    st.markdown('<div class="section-label">Neuer Eintrag</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        player = st.selectbox("Spieler", PLAYERS, index=0)
        play_date = st.date_input("Datum", value=date.today())
    with c2:
        average = st.number_input("Average (3er Schnitt)", min_value=0.0, max_value=180.0, step=0.1, format="%.1f")
        comment = st.text_input("Kommentar (optional)", placeholder="z. B. Turnier, Warm-up, starke Doppel …")

    save_disabled = average <= 0
    if st.button("➕ Eintrag speichern", use_container_width=True, type="primary", disabled=save_disabled):
        try:
            insert_average(play_date, player, average, comment)
            safe_toast(f"{player} mit {average:.1f} gespeichert", "🎯")
            st.rerun()
        except Exception as exc:
            st.error(f"Fehler beim Speichern: {exc}")

    hist_df = load_history(limit=12)
    if not hist_df.empty:
        st.markdown('<div class="section-label">Letzte Einträge</div>', unsafe_allow_html=True)
        for _, row in hist_df.iterrows():
            avatar_class = "avatar-h" if row["player"] == "Hanno" else "avatar-d"
            initial = row["player"][0]
            comment_text = row["comment"] if pd.notna(row["comment"]) and row["comment"] else "Kein Kommentar"
            html = f"""
            <div class="record-card">
                <div style="display:flex;align-items:center;gap:0.85rem;justify-content:space-between;">
                    <div style="display:flex;align-items:center;gap:0.85rem;">
                        <div class="avatar {avatar_class}">{initial}</div>
                        <div>
                            <div style="font-weight:800;">{row['player']} · {float(row['average']):.1f}</div>
                            <div class="small-muted">{row['play_date'].strftime('%d.%m.%Y')}</div>
                        </div>
                    </div>
                    <div class="small-muted">ID {int(row['id'])}</div>
                </div>
                <div class="small-muted" style="margin-top:0.6rem;">{comment_text}</div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)

with edit_tab:
    st.markdown('<div class="section-label">Vorhandene Einträge bearbeiten</div>', unsafe_allow_html=True)
    history_df = load_history(limit=30)

    if history_df.empty:
        st.info("Noch keine Einträge vorhanden.")
    else:
        history_df["label"] = history_df.apply(
            lambda r: f"ID {int(r['id'])} · {r['play_date'].strftime('%d.%m.%Y')} · {r['player']} · {float(r['average']):.1f}",
            axis=1,
        )
        selected_label = st.selectbox("Eintrag auswählen", history_df["label"].tolist())
        selected_row = history_df.loc[history_df["label"] == selected_label].iloc[0]

        edit_col1, edit_col2 = st.columns([1, 1])
        with edit_col1:
            new_avg = st.number_input(
                "Average aktualisieren",
                min_value=0.0,
                max_value=180.0,
                value=float(selected_row["average"]),
                step=0.1,
                format="%.1f",
            )
        with edit_col2:
            new_comment = st.text_input("Kommentar aktualisieren", value=selected_row["comment"] or "")

        b1, b2 = st.columns(2)
        with b1:
            if st.button("💾 Update speichern", use_container_width=True):
                try:
                    update_average(int(selected_row["id"]), new_avg, new_comment)
                    safe_toast("Eintrag aktualisiert", "✅")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Fehler beim Update: {exc}")
        with b2:
            if st.button("🗑️ Eintrag löschen", use_container_width=True):
                st.session_state.confirm_delete_id = int(selected_row["id"])

        if st.session_state.confirm_delete_id == int(selected_row["id"]):
            confirm_delete_dialog(int(selected_row["id"]), selected_label)
