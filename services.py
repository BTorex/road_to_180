from __future__ import annotations

from typing import Optional

import pandas as pd
import streamlit as st
from supabase import Client, create_client


PLAYERS = ["Hanno", "Dominik"]


@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"],
    )


def safe_toast(message: str, icon: Optional[str] = None) -> None:
    try:
        st.toast(message, icon=icon)
    except Exception:
        st.success(message)


def fetch_averages(limit: int | None = None, order_desc: bool = False) -> pd.DataFrame:
    client = get_supabase()

    query = (
        client.table("dart_averages")
        .select(
            "id, play_date, player, average, comment, darts_on_double, hits_on_double, created_at"
        )
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

    if "darts_on_double" in df.columns:
        df["darts_on_double"] = pd.to_numeric(df["darts_on_double"], errors="coerce")
    else:
        df["darts_on_double"] = pd.NA

    if "hits_on_double" in df.columns:
        df["hits_on_double"] = pd.to_numeric(df["hits_on_double"], errors="coerce")
    else:
        df["hits_on_double"] = pd.NA

    df = df.dropna(subset=["play_date", "average"]).copy()
    return df


def insert_average(
    play_date,
    player: str,
    average: float,
    comment: str | None = None,
    darts_on_double: int | None = None,
    hits_on_double: int | None = None,
):
    payload = {
        "play_date": str(play_date),
        "player": player,
        "average": float(average),
        "comment": comment or None,
        "darts_on_double": darts_on_double if darts_on_double not in (None, "") else None,
        "hits_on_double": hits_on_double if hits_on_double not in (None, "") else None,
    }

    return get_supabase().table("dart_averages").insert(payload).execute()


def update_average(
    row_id: int,
    average: float,
    comment: str | None = None,
    darts_on_double: int | None = None,
    hits_on_double: int | None = None,
):
    payload = {
        "average": float(average),
        "comment": comment or None,
        "darts_on_double": darts_on_double if darts_on_double not in (None, "") else None,
        "hits_on_double": hits_on_double if hits_on_double not in (None, "") else None,
    }

    return (
        get_supabase()
        .table("dart_averages")
        .update(payload)
        .eq("id", row_id)
        .execute()
    )


def delete_average(row_id: int):
    return (
        get_supabase()
        .table("dart_averages")
        .delete()
        .eq("id", row_id)
        .execute()
    )


def add_checkout_metrics(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    out = df.copy()
    out["checkout_rate"] = pd.NA

    valid_mask = (
        out["darts_on_double"].notna()
        & out["hits_on_double"].notna()
        & (out["darts_on_double"] > 0)
    )

    out.loc[valid_mask, "checkout_rate"] = (
        out.loc[valid_mask, "hits_on_double"] / out.loc[valid_mask, "darts_on_double"]
    ) * 100

    return out
