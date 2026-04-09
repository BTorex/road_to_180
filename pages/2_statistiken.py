from urllib.parse import quote

import pandas as pd
import plotly.express as px
import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def init_connection() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()


def load_data() -> pd.DataFrame:
    response = (
        supabase.table("dart_averages")
        .select("id, play_date, player, average, comment, created_at")
        .order("play_date")
        .order("id")
        .execute()
    )
    df = pd.DataFrame(response.data or [])
    if df.empty:
        return df
    df["play_date"] = pd.to_datetime(df["play_date"])
    df["average"] = pd.to_numeric(df["average"])
    return df


def kpis_for_player(df: pd.DataFrame, player: str) -> dict:
    p = df[df["player"] == player].sort_values(["play_date", "id"])
    if p.empty:
        return {"mean": 0.0, "median": 0.0, "form": 0.0, "max": 0.0, "min": 0.0}
    return {
        "mean": p["average"].mean(),
        "median": p["average"].median(),
        "form": p["average"].tail(5).mean(),
        "max": p["average"].max(),
        "min": p["average"].min(),
    }


def compute_head_to_head(df: pd.DataFrame) -> pd.DataFrame:
    day_player = df.groupby(["play_date", "player"], as_index=False)["average"].mean()
    pivot = day_player.pivot(index="play_date", columns="player", values="average").dropna()
    if pivot.empty:
        return pd.DataFrame({"player": ["Hanno", "Dominik"], "wins": [0, 0]})
    hanno_wins = int((pivot["Hanno"] > pivot["Dominik"]).sum())
    dominik_wins = int((pivot["Dominik"] > pivot["Hanno"]).sum())
    return pd.DataFrame({"player": ["Hanno", "Dominik"], "wins": [hanno_wins, dominik_wins]})


def make_line_chart(df: pd.DataFrame):
    chart_df = df.sort_values(["play_date", "id"]).copy()
    chart_df["sma10"] = chart_df.groupby("player")["average"].transform(lambda s: s.rolling(10, min_periods=1).mean())
    fig = px.line(
        chart_df,
        x="play_date",
        y="sma10",
        color="player",
        color_discrete_map={"Hanno": "#4da3ff", "Dominik": "#ff9d4d"},
        markers=True,
        title="Form-Kurve (SMA 10)",
    )
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend_title=None, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def make_histogram(df: pd.DataFrame):
    fig = px.histogram(
        df,
        x="average",
        color="player",
        nbins=16,
        barmode="overlay",
        opacity=0.68,
        color_discrete_map={"Hanno": "#4da3ff", "Dominik": "#ff9d4d"},
        title="Barrieren-Analyse",
    )
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=50, b=10))
    return fig


def make_daily_progression(df: pd.DataFrame):
    chart_df = df.sort_values(["play_date", "id"]).copy()
    chart_df["lag_number"] = chart_df.groupby(["play_date", "player"]).cumcount() + 1
    grouped = chart_df.groupby(["player", "lag_number"], as_index=False)["average"].mean()
    fig = px.line(
        grouped,
        x="lag_number",
        y="average",
        color="player",
        markers=True,
        color_discrete_map={"Hanno": "#4da3ff", "Dominik": "#ff9d4d"},
        title="Tagesverlauf (Warm-up vs. Ermüdung)",
    )
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=50, b=10))
    fig.update_xaxes(dtick=1, title="Lag-Nummer")
    return fig


def df_to_csv_download(df: pd.DataFrame) -> bytes:
    export_df = df.copy()
    export_df["play_date"] = export_df["play_date"].dt.strftime("%Y-%m-%d")
    return export_df.to_csv(index=False, sep=";", encoding="utf-8-sig").encode("utf-8-sig")


st.markdown('<div class="page-title">Statistische Auswertung</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Filter, KPIs, Head-to-Head und Export für eure Darts-Averages.</div>', unsafe_allow_html=True)

df = load_data()
if df.empty:
    st.info("Noch keine Daten vorhanden. Bitte zuerst Einträge erfassen.")
    st.stop()

min_date = df["play_date"].min().date()
max_date = df["play_date"].max().date()
date_range = st.date_input("Zeitraum", value=(min_date, max_date), min_value=min_date, max_value=max_date)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = min_date
    end_date = max_date

filtered = df[(df["play_date"].dt.date >= start_date) & (df["play_date"].dt.date <= end_date)].copy()

kpi_h = kpis_for_player(filtered, "Hanno")
kpi_d = kpis_for_player(filtered, "Dominik")

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("Hanno Ø", f"{kpi_h['mean']:.1f}")
with c2:
    st.metric("Dominik Ø", f"{kpi_d['mean']:.1f}")
with c3:
    st.metric("Median Hanno", f"{kpi_h['median']:.1f}")
with c4:
    st.metric("Median Dominik", f"{kpi_d['median']:.1f}")
with c5:
    st.metric("Zeitraum-Spiele", f"{len(filtered)}")

c6, c7, c8, c9 = st.columns(4)
with c6:
    st.metric("Form Hanno", f"{kpi_h['form']:.1f}")
with c7:
    st.metric("Form Dominik", f"{kpi_d['form']:.1f}")
with c8:
    st.metric("High Hanno", f"{kpi_h['max']:.1f}")
with c9:
    st.metric("High Dominik", f"{kpi_d['max']:.1f}")

st.markdown('<div class="section-label">Head-to-Head</div>', unsafe_allow_html=True)
h2h = compute_head_to_head(filtered)
bar_fig = px.bar(
    h2h,
    x="player",
    y="wins",
    color="player",
    text="wins",
    color_discrete_map={"Hanno": "#4da3ff", "Dominik": "#ff9d4d"},
)
bar_fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
st.plotly_chart(bar_fig, use_container_width=True)

left, right = st.columns(2)
with left:
    st.plotly_chart(make_line_chart(filtered), use_container_width=True)
    st.plotly_chart(make_daily_progression(filtered), use_container_width=True)
with right:
    st.plotly_chart(make_histogram(filtered), use_container_width=True)

st.markdown('<div class="section-label">Export</div>', unsafe_allow_html=True)
mail_subject = quote("Road to 180 – Statistik-Zusammenfassung")
mail_body = quote(
    f"Zeitraum: {start_date} bis {end_date}\n"
    f"Hanno Ø: {kpi_h['mean']:.1f}\n"
    f"Dominik Ø: {kpi_d['mean']:.1f}\n"
    f"Tagessiege Hanno: {int(h2h.loc[h2h['player']=='Hanno','wins'].iloc[0])}\n"
    f"Tagessiege Dominik: {int(h2h.loc[h2h['player']=='Dominik','wins'].iloc[0])}"
)
mailto_link = f"mailto:?subject={mail_subject}&body={mail_body}"

ex1, ex2 = st.columns(2)
with ex1:
    st.download_button("CSV herunterladen", data=df_to_csv_download(filtered), file_name="road_to_180_export.csv", mime="text/csv", use_container_width=True)
with ex2:
    st.link_button("Per E-Mail teilen", mailto_link, use_container_width=True)
