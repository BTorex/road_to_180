
from urllib.parse import quote
import pandas as pd
import plotly.express as px
import streamlit as st
from services import fetch_averages, format_date_de

def kpis_for_player(df: pd.DataFrame, player: str) -> dict:
    p = df[df["player"] == player].sort_values(["play_date", "id"])
    if p.empty:
        return {"mean": 0.0, "median": 0.0, "form5": 0.0, "max": 0.0, "min": 0.0, "count": 0, "std": 0.0, "morning": 0.0, "evening": 0.0}
    created = p.dropna(subset=["created_at"]).copy()
    morning = created[created["created_at"].dt.hour < 18]["average"].mean() if not created.empty else 0.0
    evening = created[created["created_at"].dt.hour >= 18]["average"].mean() if not created.empty else 0.0
    return {
        "mean": p["average"].mean(),
        "median": p["average"].median(),
        "form5": p["average"].tail(5).mean(),
        "max": p["average"].max(),
        "min": p["average"].min(),
        "count": len(p),
        "std": p["average"].std(ddof=0) if len(p) > 1 else 0.0,
        "morning": 0.0 if pd.isna(morning) else morning,
        "evening": 0.0 if pd.isna(evening) else evening,
    }

def compute_head_to_head(df: pd.DataFrame) -> pd.DataFrame:
    per_day = df.groupby(["play_date", "player"], as_index=False)["average"].mean()
    pivot = per_day.pivot(index="play_date", columns="player", values="average")
    if "Hanno" not in pivot.columns:
        pivot["Hanno"] = pd.NA
    if "Dominik" not in pivot.columns:
        pivot["Dominik"] = pd.NA
    pivot = pivot.dropna(subset=["Hanno", "Dominik"])
    return pd.DataFrame({
        "player": ["Hanno", "Dominik"],
        "wins": [int((pivot["Hanno"] > pivot["Dominik"]).sum()), int((pivot["Dominik"] > pivot["Hanno"]).sum())],
    })

def make_form_chart(df: pd.DataFrame):
    chart_df = df.sort_values(["play_date", "id"]).copy()
    chart_df["sma10"] = chart_df.groupby("player")["average"].transform(lambda s: s.rolling(10, min_periods=1).mean())
    fig = px.line(chart_df, x="play_date", y="sma10", color="player", markers=True, title="Form-Kurve", color_discrete_map={"Hanno": "#5aa8ff", "Dominik": "#ffab66"})
    fig.update_traces(line=dict(width=3), marker=dict(size=7))
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.02)", legend_title=None, margin=dict(l=10, r=10, t=50, b=10), height=360)
    fig.update_xaxes(title=None, gridcolor='rgba(255,255,255,0.06)')
    fig.update_yaxes(title='Average', gridcolor='rgba(255,255,255,0.06)')
    return fig

def make_hist_chart(df: pd.DataFrame):
    fig = px.histogram(df, x="average", color="player", nbins=18, barmode="overlay", opacity=0.72, title="Verteilung", color_discrete_map={"Hanno": "#5aa8ff", "Dominik": "#ffab66"})
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.02)", margin=dict(l=10, r=10, t=50, b=10), height=340)
    fig.update_xaxes(title='Average', gridcolor='rgba(255,255,255,0.06)')
    fig.update_yaxes(title='Häufigkeit', gridcolor='rgba(255,255,255,0.06)')
    return fig

def make_time_chart(df: pd.DataFrame):
    cdf = df.dropna(subset=['created_at']).copy()
    if cdf.empty:
        return None
    cdf['hour'] = cdf['created_at'].dt.hour
    grouped = cdf.groupby(['player','hour'], as_index=False)['average'].mean()
    fig = px.line(grouped, x='hour', y='average', color='player', markers=True, title='Leistung nach Uhrzeit', color_discrete_map={"Hanno": "#5aa8ff", "Dominik": "#ffab66"})
    fig.update_traces(line=dict(width=3), marker=dict(size=7))
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.02)', margin=dict(l=10, r=10, t=50, b=10), height=340, legend_title=None)
    fig.update_xaxes(title='Stunde', dtick=1, gridcolor='rgba(255,255,255,0.06)')
    fig.update_yaxes(title='Ø Average', gridcolor='rgba(255,255,255,0.06)')
    return fig

def make_consistency_chart(df: pd.DataFrame):
    summary = df.groupby("player", as_index=False).agg(std_dev=("average", "std"))
    summary["std_dev"] = summary["std_dev"].fillna(0)
    fig = px.bar(summary, x="player", y="std_dev", color="player", title="Konstanz", color_discrete_map={"Hanno": "#5aa8ff", "Dominik": "#ffab66"}, text_auto='.1f')
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.02)", showlegend=False, margin=dict(l=10, r=10, t=50, b=10), height=320)
    fig.update_yaxes(title='Std.-Abweichung', gridcolor='rgba(255,255,255,0.06)')
    return fig

def build_mailto(start_date, end_date, kpi_h, kpi_d):
    lines = [
        f"Zeitraum: {start_date.strftime('%d.%m.%Y')} bis {end_date.strftime('%d.%m.%Y')}",
        f"Hanno Ø: {kpi_h['mean']:.1f}",
        f"Dominik Ø: {kpi_d['mean']:.1f}",
        f"Hanno Bestwert: {kpi_h['max']:.1f}",
        f"Dominik Bestwert: {kpi_d['max']:.1f}",
    ]
    return f"mailto:?subject={quote('Road to 180 – Statistik-Zusammenfassung')}&body={quote(chr(10).join(lines))}"

def df_to_csv_download(df: pd.DataFrame) -> bytes:
    export_df = df.copy()
    export_df['play_date'] = export_df['play_date'].dt.strftime('%d.%m.%Y')
    export_df['created_at'] = export_df['created_at'].dt.strftime('%d.%m.%Y %H:%M')
    return export_df.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')

st.markdown('<div class="page-title">Statistiken</div>', unsafe_allow_html=True)

df = fetch_averages()
if df.empty:
    st.info("Noch keine Daten vorhanden. Bitte zuerst Einträge erfassen.")
    st.stop()

min_date = df["play_date"].min().date()
max_date = df["play_date"].max().date()
selected_range = st.date_input("Zeitraum", value=(min_date, max_date), min_value=min_date, max_value=max_date)
if isinstance(selected_range, tuple) and len(selected_range) == 2:
    start_date, end_date = selected_range
else:
    start_date, end_date = min_date, max_date

filtered = df[(df["play_date"].dt.date >= start_date) & (df["play_date"].dt.date <= end_date)].copy()
if filtered.empty:
    st.warning("Im gewählten Zeitraum liegen keine Daten vor.")
    st.stop()

kpi_h = kpis_for_player(filtered, "Hanno")
kpi_d = kpis_for_player(filtered, "Dominik")
h2h = compute_head_to_head(filtered)

st.markdown('<div class="section-label">Leistung</div>', unsafe_allow_html=True)
row1 = st.columns(4)
for col, label, value in [
    (row1[0], "Hanno Ø", f"{kpi_h['mean']:.1f}"),
    (row1[1], "Dominik Ø", f"{kpi_d['mean']:.1f}"),
    (row1[2], "Hanno Form 5", f"{kpi_h['form5']:.1f}"),
    (row1[3], "Dominik Form 5", f"{kpi_d['form5']:.1f}"),
]:
    with col:
        st.metric(label, value)

st.markdown('<div class="section-label">Qualität</div>', unsafe_allow_html=True)
row2 = st.columns(4)
for col, label, value in [
    (row2[0], "Hanno High", f"{kpi_h['max']:.1f}"),
    (row2[1], "Dominik High", f"{kpi_d['max']:.1f}"),
    (row2[2], "Hanno Konstanz", f"{kpi_h['std']:.1f}"),
    (row2[3], "Dominik Konstanz", f"{kpi_d['std']:.1f}"),
]:
    with col:
        st.metric(label, value)

st.markdown('<div class="section-label">Zeitmuster</div>', unsafe_allow_html=True)
row3 = st.columns(4)
for col, label, value in [
    (row3[0], "Hanno tagsüber", f"{kpi_h['morning']:.1f}" if kpi_h['morning'] else '—'),
    (row3[1], "Hanno abends", f"{kpi_h['evening']:.1f}" if kpi_h['evening'] else '—'),
    (row3[2], "Dominik tagsüber", f"{kpi_d['morning']:.1f}" if kpi_d['morning'] else '—'),
    (row3[3], "Dominik abends", f"{kpi_d['evening']:.1f}" if kpi_d['evening'] else '—'),
]:
    with col:
        st.metric(label, value)

st.markdown('<div class="section-label">Vergleich</div>', unsafe_allow_html=True)
fig_h2h = px.bar(h2h, x="player", y="wins", color="player", text="wins", color_discrete_map={"Hanno": "#5aa8ff", "Dominik": "#ffab66"}, title='Head-to-Head nach Spieltag')
fig_h2h.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.02)", showlegend=False, margin=dict(l=10, r=10, t=50, b=10), height=320)
fig_h2h.update_yaxes(title='Tagessiege', gridcolor='rgba(255,255,255,0.06)')
st.plotly_chart(fig_h2h, use_container_width=True)

c1, c2 = st.columns([1.1, 0.9])
with c1:
    st.plotly_chart(make_form_chart(filtered), use_container_width=True)
    time_fig = make_time_chart(filtered)
    if time_fig is not None:
        st.plotly_chart(time_fig, use_container_width=True)
with c2:
    st.plotly_chart(make_hist_chart(filtered), use_container_width=True)
    st.plotly_chart(make_consistency_chart(filtered), use_container_width=True)

st.markdown('<div class="section-label">Export</div>', unsafe_allow_html=True)
mailto_link = build_mailto(start_date, end_date, kpi_h, kpi_d)
ex1, ex2 = st.columns(2)
with ex1:
    st.download_button("CSV herunterladen", data=df_to_csv_download(filtered), file_name="road_to_180_export.csv", mime="text/csv", use_container_width=True)
with ex2:
    st.link_button("Per E-Mail teilen", mailto_link, use_container_width=True)
