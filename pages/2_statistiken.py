from urllib.parse import quote

import pandas as pd
import plotly.express as px
import streamlit as st

from services import add_checkout_metrics, fetch_averages, safe_toast


def kpis_for_player(df: pd.DataFrame, player: str) -> dict:
    p = df[df["player"] == player].sort_values(["play_date", "id"])
    if p.empty:
        return {"mean": 0.0, "median": 0.0, "form": 0.0, "max": 0.0, "min": 0.0, "count": 0, "checkout": None}
    checkout = p["checkout_rate"].dropna().mean() if "checkout_rate" in p.columns else None
    return {
        "mean": p["average"].mean(),
        "median": p["average"].median(),
        "form": p["average"].tail(5).mean(),
        "max": p["average"].max(),
        "min": p["average"].min(),
        "count": len(p),
        "checkout": checkout,
    }


def compute_head_to_head(df: pd.DataFrame) -> pd.DataFrame:
    per_day_player = df.groupby(["play_date", "player"], as_index=False)["average"].mean()
    pivot = per_day_player.pivot(index="play_date", columns="player", values="average")
    if "Hanno" not in pivot.columns:
        pivot["Hanno"] = pd.NA
    if "Dominik" not in pivot.columns:
        pivot["Dominik"] = pd.NA
    pivot = pivot.dropna(subset=["Hanno", "Dominik"])
    hanno_wins = int((pivot["Hanno"] > pivot["Dominik"]).sum())
    dominik_wins = int((pivot["Dominik"] > pivot["Hanno"]).sum())
    return pd.DataFrame({"player": ["Hanno", "Dominik"], "wins": [hanno_wins, dominik_wins]})


def make_line_chart(df: pd.DataFrame):
    chart_df = df.sort_values(["play_date", "id"]).copy()
    chart_df["sma10"] = chart_df.groupby("player")["average"].transform(lambda s: s.rolling(10, min_periods=1).mean())
    fig = px.line(chart_df, x="play_date", y="sma10", color="player", markers=True, color_discrete_map={"Hanno": "#4da3ff", "Dominik": "#ff9d4d"}, title="Form-Kurve (SMA 10)")
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=50, b=10), legend_title=None)
    return fig


def make_histogram(df: pd.DataFrame):
    fig = px.histogram(df, x="average", color="player", nbins=16, barmode="overlay", opacity=0.68, color_discrete_map={"Hanno": "#4da3ff", "Dominik": "#ff9d4d"}, title="Barrieren-Analyse")
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=50, b=10))
    return fig


def make_daily_progression(df: pd.DataFrame):
    chart_df = df.sort_values(["play_date", "id"]).copy()
    chart_df["lag_number"] = chart_df.groupby(["play_date", "player"]).cumcount() + 1
    grouped = chart_df.groupby(["player", "lag_number"], as_index=False)["average"].mean()
    fig = px.line(grouped, x="lag_number", y="average", color="player", markers=True, color_discrete_map={"Hanno": "#4da3ff", "Dominik": "#ff9d4d"}, title="Tagesverlauf (Warm-up vs. Ermüdung)")
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=50, b=10))
    fig.update_xaxes(dtick=1, title="Lag-Nummer")
    return fig


def make_checkout_chart(df: pd.DataFrame):
    cdf = df.dropna(subset=["checkout_rate"]).copy()
    if cdf.empty:
        return None
    summary = cdf.groupby("player", as_index=False)["checkout_rate"].mean()
    fig = px.bar(summary, x="player", y="checkout_rate", color="player", text_auto='.1f', color_discrete_map={"Hanno": "#4da3ff", "Dominik": "#ff9d4d"}, title="Ø Doppelquote")
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, margin=dict(l=10, r=10, t=50, b=10))
    fig.update_yaxes(title="Prozent")
    return fig


def df_to_csv_download(df: pd.DataFrame) -> bytes:
    export_df = df.copy()
    export_df["play_date"] = export_df["play_date"].dt.strftime("%Y-%m-%d")
    return export_df.to_csv(index=False, sep=";", encoding="utf-8-sig").encode("utf-8-sig")


st.markdown('<div class="page-title">Statistische Auswertung</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">KPI-Ansicht mit Checkout-Tracking, Head-to-Head pro Kalendertag und CSV-/Mail-Export.</div>', unsafe_allow_html=True)

df = add_checkout_metrics(fetch_averages())
if df.empty:
    st.info("Noch keine Daten vorhanden. Bitte zuerst Einträge erfassen.")
    st.stop()

min_date = df["play_date"].min().date()
max_date = df["play_date"].max().date()
date_range = st.date_input("Zeitraum", value=(min_date, max_date), min_value=min_date, max_value=max_date)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = df[(df["play_date"].dt.date >= start_date) & (df["play_date"].dt.date <= end_date)].copy()
if filtered.empty:
    st.warning("Im gewählten Zeitraum liegen keine Daten vor.")
    st.stop()

kpi_h = kpis_for_player(filtered, "Hanno")
kpi_d = kpis_for_player(filtered, "Dominik")

row1 = st.columns(5)
for col, label, value in [
    (row1[0], "Hanno Ø", f"{kpi_h['mean']:.1f}"),
    (row1[1], "Dominik Ø", f"{kpi_d['mean']:.1f}"),
    (row1[2], "Median Hanno", f"{kpi_h['median']:.1f}"),
    (row1[3], "Median Dominik", f"{kpi_d['median']:.1f}"),
    (row1[4], "Zeitraum-Spiele", f"{len(filtered)}"),
]:
    with col:
        st.metric(label, value)

row2 = st.columns(4)
for col, label, value in [
    (row2[0], "Form Hanno", f"{kpi_h['form']:.1f}"),
    (row2[1], "Form Dominik", f"{kpi_d['form']:.1f}"),
    (row2[2], "Checkout Hanno", f"{kpi_h['checkout']:.1f}%" if kpi_h['checkout'] is not None else "—"),
    (row2[3], "Checkout Dominik", f"{kpi_d['checkout']:.1f}%" if kpi_d['checkout'] is not None else "—"),
]:
    with col:
        st.metric(label, value)

st.markdown('<div class="section-label">Head-to-Head</div>', unsafe_allow_html=True)
h2h = compute_head_to_head(filtered)
h2h_fig = px.bar(h2h, x="player", y="wins", color="player", text="wins", color_discrete_map={"Hanno": "#4da3ff", "Dominik": "#ff9d4d"})
h2h_fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
st.plotly_chart(h2h_fig, use_container_width=True)

left, right = st.columns([1.15, 0.85])
with left:
    st.plotly_chart(make_line_chart(filtered), use_container_width=True)
    st.plotly_chart(make_daily_progression(filtered), use_container_width=True)
with right:
    st.plotly_chart(make_histogram(filtered), use_container_width=True)
    checkout_fig = make_checkout_chart(filtered)
    if checkout_fig is not None:
        st.plotly_chart(checkout_fig, use_container_width=True)
    else:
        st.info("Noch keine Checkout-Daten vorhanden.")

st.markdown('<div class="section-label">Export</div>', unsafe_allow_html=True)
mail_subject = quote("Road to 180 – Statistik-Zusammenfassung")
mail_body = quote(
    f"Zeitraum: {start_date} bis {end_date}
"
    f"Hanno Ø: {kpi_h['mean']:.1f}
"
    f"Dominik Ø: {kpi_d['mean']:.1f}
"
    f"Checkout Hanno: {kpi_h['checkout']:.1f}%
" if kpi_h['checkout'] is not None else f"Checkout Hanno: —
"
)
mail_body += quote(
    f"Checkout Dominik: {kpi_d['checkout']:.1f}%
" if kpi_d['checkout'] is not None else "Checkout Dominik: —
"
)
mailto_link = f"mailto:?subject={mail_subject}&body={mail_body}"

ex1, ex2 = st.columns(2)
with ex1:
    st.download_button("CSV herunterladen", data=df_to_csv_download(filtered), file_name="road_to_180_export.csv", mime="text/csv", use_container_width=True)
with ex2:
    if st.link_button("Per E-Mail teilen", mailto_link, use_container_width=True):
        safe_toast("Mail-Entwurf geöffnet", "📧")
