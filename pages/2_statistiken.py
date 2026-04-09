from urllib.parse import quote
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from services import fetch_averages, format_date_de

def player_df(df: pd.DataFrame, player: str) -> pd.DataFrame:
    return df[df['player'] == player].sort_values(['play_date', 'created_at', 'id']).copy()

def rolling_improvement(pdf: pd.DataFrame, window: int = 5) -> float:
    if len(pdf) < window * 2:
        return np.nan
    roll = pdf['average'].rolling(window, min_periods=window).mean().dropna()
    if len(roll) < 2:
        return np.nan
    return float(roll.iloc[-1] - roll.iloc[0])

def streak_info(pdf: pd.DataFrame):
    if len(pdf) < 2:
        return ('—', 0)
    diffs = pdf['average'].diff().fillna(0)
    state = []
    for d in diffs.iloc[1:]:
        if d > 0:
            state.append('hot')
        elif d < 0:
            state.append('cold')
        else:
            state.append('flat')
    if not state:
        return ('—', 0)
    current = state[-1]
    if current == 'flat':
        return ('neutral', 1)
    count = 1
    for s in reversed(state[:-1]):
        if s == current:
            count += 1
        else:
            break
    return (current, count)

def best_of_day(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(['play_date','player'], as_index=False)['average'].max().sort_values(['play_date','average'], ascending=[True, False])

def session_compare(df: pd.DataFrame) -> pd.DataFrame:
    cdf = df.dropna(subset=['created_at']).copy()
    if cdf.empty:
        return pd.DataFrame(columns=['player','session','average'])
    cdf['session'] = pd.cut(cdf['created_at'].dt.hour, bins=[-1,11,17,23], labels=['Vormittag','Nachmittag','Abend'])
    return cdf.groupby(['player','session'], as_index=False)['average'].mean()

def kpi_block(title: str, items):
    html = '<div class="glass-card"><div class="kicker">' + title + '</div><div class="mini-grid">'
    for label, value in items:
        html += f'<div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:18px;padding:.85rem .9rem;"><div class="small-muted">{label}</div><div style="font-size:1.45rem;font-weight:800;letter-spacing:-.03em;">{value}</div></div>'
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

def make_form_chart(df: pd.DataFrame):
    chart_df = df.sort_values(['play_date', 'created_at', 'id']).copy()
    chart_df['sma5'] = chart_df.groupby('player')['average'].transform(lambda s: s.rolling(5, min_periods=1).mean())
    fig = px.line(chart_df, x='play_date', y='sma5', color='player', markers=True, title='Rolling Form (5)', color_discrete_map={'Hanno':'#5aa8ff','Dominik':'#ffab66'})
    fig.update_traces(line=dict(width=3), marker=dict(size=7))
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.02)', height=360, margin=dict(l=10,r=10,t=50,b=10), legend_title=None)
    fig.update_xaxes(title=None, gridcolor='rgba(255,255,255,0.06)')
    fig.update_yaxes(title='Ø Average', gridcolor='rgba(255,255,255,0.06)')
    return fig

def make_best_day_chart(df: pd.DataFrame):
    best = best_of_day(df)
    fig = px.bar(best, x='play_date', y='average', color='player', barmode='group', title='Best of Day', color_discrete_map={'Hanno':'#5aa8ff','Dominik':'#ffab66'})
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.02)', height=340, margin=dict(l=10,r=10,t=50,b=10), legend_title=None)
    fig.update_xaxes(title=None, gridcolor='rgba(255,255,255,0.06)')
    fig.update_yaxes(title='Tagesbestwert', gridcolor='rgba(255,255,255,0.06)')
    return fig

def make_streak_chart(df: pd.DataFrame):
    records = []
    for player in ['Hanno','Dominik']:
        pdf = player_df(df, player)
        running = 0
        prev = None
        for _, row in pdf.iterrows():
            val = row['average']
            if prev is None:
                running = 0
            else:
                if val > prev:
                    running = running + 1 if running >= 0 else 1
                elif val < prev:
                    running = running - 1 if running <= 0 else -1
                else:
                    running = 0
            prev = val
            records.append({'player': player, 'play_date': row['play_date'], 'streak': running})
    sdf = pd.DataFrame(records)
    fig = px.bar(sdf, x='play_date', y='streak', color='player', barmode='group', title='Hot / Cold Streaks', color_discrete_map={'Hanno':'#5aa8ff','Dominik':'#ffab66'})
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.02)', height=340, margin=dict(l=10,r=10,t=50,b=10), legend_title=None)
    fig.update_yaxes(title='Serie (+ heiß / - kalt)', gridcolor='rgba(255,255,255,0.06)')
    return fig

def make_session_chart(df: pd.DataFrame):
    sdf = session_compare(df)
    if sdf.empty:
        return None
    fig = px.bar(sdf, x='session', y='average', color='player', barmode='group', title='Session-Vergleich', color_discrete_map={'Hanno':'#5aa8ff','Dominik':'#ffab66'}, category_orders={'session':['Vormittag','Nachmittag','Abend']})
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(255,255,255,0.02)', height=340, margin=dict(l=10,r=10,t=50,b=10), legend_title=None)
    fig.update_yaxes(title='Ø Average', gridcolor='rgba(255,255,255,0.06)')
    return fig

def build_mailto(start_date, end_date, h_df, d_df):
    h_imp = rolling_improvement(h_df)
    d_imp = rolling_improvement(d_df)
    lines = [
        f"Zeitraum: {start_date.strftime('%d.%m.%Y')} bis {end_date.strftime('%d.%m.%Y')}",
        f"Hanno Rolling Improvement: {'—' if pd.isna(h_imp) else f'{h_imp:+.1f}'}",
        f"Dominik Rolling Improvement: {'—' if pd.isna(d_imp) else f'{d_imp:+.1f}'}",
    ]
    return f"mailto:?subject={quote('Road to 180 – V6 Statistik')}&body={quote(chr(10).join(lines))}"

st.markdown('<div class="page-title">Statistiken</div>', unsafe_allow_html=True)
df = fetch_averages()
if df.empty:
    st.info('Noch keine Daten vorhanden. Bitte zuerst Einträge erfassen.')
    st.stop()

min_date = df['play_date'].min().date()
max_date = df['play_date'].max().date()
selected_range = st.date_input('Zeitraum', value=(min_date, max_date), min_value=min_date, max_value=max_date)
if isinstance(selected_range, tuple) and len(selected_range) == 2:
    start_date, end_date = selected_range
else:
    start_date, end_date = min_date, max_date

filtered = df[(df['play_date'].dt.date >= start_date) & (df['play_date'].dt.date <= end_date)].copy()
if filtered.empty:
    st.warning('Im gewählten Zeitraum liegen keine Daten vor.')
    st.stop()

h_df = player_df(filtered, 'Hanno')
d_df = player_df(filtered, 'Dominik')
top_h = h_df['average'].max() if not h_df.empty else np.nan
top_d = d_df['average'].max() if not d_df.empty else np.nan
form_h = h_df['average'].tail(5).mean() if not h_df.empty else np.nan
form_d = d_df['average'].tail(5).mean() if not d_df.empty else np.nan
roll_h = rolling_improvement(h_df)
roll_d = rolling_improvement(d_df)
streak_h, streak_h_n = streak_info(h_df)
streak_d, streak_d_n = streak_info(d_df)

hero_left, hero_right = st.columns([1.15, 0.85])
with hero_left:
    leader = 'Hanno' if np.nan_to_num(form_h) >= np.nan_to_num(form_d) else 'Dominik'
    leader_form = form_h if leader == 'Hanno' else form_d
    leader_delta = roll_h if leader == 'Hanno' else roll_d
    hero_delta = '—' if pd.isna(leader_delta) else f'{leader_delta:+.1f}'
    hero_html = f"<div class='hero-kpi'><div class='kicker'>Aktuelle Form-Führung</div><div class='hero-value'>{leader_form:.1f}</div><div class='hero-meta'>{leader} · Form 5 · Rolling Improvement {hero_delta}</div></div>"
    st.markdown(hero_html, unsafe_allow_html=True)
with hero_right:
    latest_day = format_date_de(filtered['play_date'].max())
    total_sessions = len(filtered)
    period_html = f"<div class='glass-card'><div class='kicker'>Zeitraum</div><div style='font-size:1.4rem;font-weight:800;'>{latest_day}</div><div class='hero-meta'>Letzter Spieltag · {total_sessions} Einträge im Filter</div></div>"
    st.markdown(period_html, unsafe_allow_html=True)

kpi_block('Leistung', [
    ('Hanno Best-of-Day', '—' if h_df.empty else f"{h_df.groupby('play_date')['average'].max().mean():.1f}"),
    ('Dominik Best-of-Day', '—' if d_df.empty else f"{d_df.groupby('play_date')['average'].max().mean():.1f}"),
    ('Hanno Rolling Improvement', '—' if pd.isna(roll_h) else f"{roll_h:+.1f}"),
    ('Dominik Rolling Improvement', '—' if pd.isna(roll_d) else f"{roll_d:+.1f}"),
])

kpi_block('Serien', [
    ('Hanno Streak', f"{streak_h} · {streak_h_n}"),
    ('Dominik Streak', f"{streak_d} · {streak_d_n}"),
    ('Hanno High', '—' if pd.isna(top_h) else f"{top_h:.1f}"),
    ('Dominik High', '—' if pd.isna(top_d) else f"{top_d:.1f}"),
])

chart_a, chart_b = st.columns([1.1, 0.9])
with chart_a:
    st.plotly_chart(make_form_chart(filtered), use_container_width=True)
    st.plotly_chart(make_best_day_chart(filtered), use_container_width=True)
with chart_b:
    st.plotly_chart(make_streak_chart(filtered), use_container_width=True)
    sess_fig = make_session_chart(filtered)
    if sess_fig is not None:
        st.plotly_chart(sess_fig, use_container_width=True)

st.markdown('<div class="section-label">Export</div>', unsafe_allow_html=True)
export_df = filtered.copy()
export_df['play_date'] = export_df['play_date'].dt.strftime('%d.%m.%Y')
export_df['created_at'] = export_df['created_at'].dt.strftime('%d.%m.%Y %H:%M')
ex1, ex2 = st.columns(2)
with ex1:
    st.download_button('CSV herunterladen', data=export_df.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig'), file_name='road_to_180_v6_stats.csv', mime='text/csv', use_container_width=True)
with ex2:
    st.link_button('Per E-Mail teilen', build_mailto(start_date, end_date, h_df, d_df), use_container_width=True)
