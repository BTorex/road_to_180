
from pathlib import Path
from typing import Optional
import pandas as pd
import streamlit as st
from supabase import Client, create_client

PLAYERS = ["Hanno", "Dominik"]
STATIC = Path(__file__).parent / "static"

@st.cache_resource
def get_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def safe_toast(message: str, icon: Optional[str] = None) -> None:
    try:
        st.toast(message, icon=icon)
    except Exception:
        st.success(message)

def fetch_averages(limit: int | None = None, order_desc: bool = False) -> pd.DataFrame:
    query = (
        get_supabase().table("dart_averages")
        .select("id, play_date, player, average, comment, created_at")
        .order("play_date", desc=order_desc)
        .order("id", desc=order_desc)
    )
    if limit is not None:
        query = query.limit(limit)
    response = query.execute()
    df = pd.DataFrame(response.data or [])
    if df.empty:
        return df
    df["play_date"] = pd.to_datetime(df["play_date"], errors="coerce")
    df["average"] = pd.to_numeric(df["average"], errors="coerce")
    return df.dropna(subset=["play_date", "average"]).copy()

def insert_average(play_date, player: str, average: float, comment: str | None = None):
    payload = {
        "play_date": str(play_date),
        "player": player,
        "average": float(average),
        "comment": comment or None,
    }
    return get_supabase().table("dart_averages").insert(payload).execute()

def update_average(row_id: int, average: float, comment: str | None = None):
    payload = {"average": float(average), "comment": comment or None}
    return get_supabase().table("dart_averages").update(payload).eq("id", row_id).execute()

def delete_average(row_id: int):
    return get_supabase().table("dart_averages").delete().eq("id", row_id).execute()

def player_image(player: str) -> str | None:
    filename = "hanno.png" if player == "Hanno" else "dominik.png"
    path = STATIC / filename
    return str(path) if path.exists() else None
