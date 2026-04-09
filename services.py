from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd
import streamlit as st
from supabase import Client, create_client

PLAYERS = ["Hanno", "Dominik"]


@dataclass
class AppConfig:
    supabase_url: str
    supabase_key: str


@st.cache_resource
def get_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def safe_toast(msg: str, icon: Optional[str] = None):
    try:
        st.toast(msg, icon=icon)
    except Exception:
        st.success(msg)


def fetch_averages(limit: int | None = None, order_desc: bool = False) -> pd.DataFrame:
    client = get_supabase()
    query = client.table("dart_averages").select("id, play_date, player, average, comment, darts_on_double, hits_on_double, created_at")
    query = query.order("play_date", desc=order_desc).order("id", desc=order_desc)
    if limit:
        query = query.limit(limit)
    response = query.execute()
    df = pd.DataFrame(response.data or [])
    if df.empty:
        return df
    df["play_date"] = pd.to_datetime(df["play_date"])
    df["average"] = pd.to_numeric(df["average"], errors="coerce")
    if "darts_on_double" in df.columns:
        df["darts_on_double"] = pd.to_numeric(df["darts_on_double"], errors="coerce")
    else:
        df["darts_on_double"] = pd.NA
    if "hits_on_double" in df.columns:
        df["hits_on_double"] = pd.to_numeric(df["hits_on_double"], errors="coerce")
    else:
        df["hits_on_double"] = pd.NA
    df = df.dropna(subset=["average"])
    return df


def insert_average(play_date, player, average, comment=None, darts_on_double=None, hits_on_double=None):
    payload = {
        "play_date": str(play_date),
        "player": player,
        "average": float(average),
        "comment": comment or None,
        "darts_on_double": darts_on_double if darts_on_double not in (None, "") else None,
        "hits_on_double": hits_on_double if hits_on_double not in (None, "") else None,
    }
    return get_supabase().table("dart_averages").insert(payload).execute()


def update_average(row_id, average, comment=None, darts_on_double=None, hits_on_double=None):
    payload = {
        "average": float(average),
        "comment": comment or None,
        "darts_on_double": darts_on_double if darts_on_double not in (None, "") else None,
        "hits_on_double": hits_on_double if hits_on_double not in (None, "") else None,
    }
    return get_supabase().table("dart_averages").update(payload).eq("id", row_id).execute()


def delete_average(row_id):
    return get_supabase().table("dart_averages").delete().eq("id", row_id).execute()


def add_checkout_metrics(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    valid = out["darts_on_double"].fillna(0) > 0
    out["checkout_rate"] = pd.NA
    out.loc[valid, "checkout_rate"] = (out.loc[valid, "hits_on_double"] / out.loc[valid, "darts_on_double"]) * 100
    return out
