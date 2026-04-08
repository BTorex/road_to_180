# --- CHARTS ---
st.subheader("📈 Entwicklung über Zeit")

df_filtered['Datum'] = df_filtered['play_date'].dt.strftime('%d.%m.%Y')
df_filtered = df_filtered.rename(columns={"average": "3er Schnitt", "player": "Spieler"})

fig_line = px.line(df_filtered, x='play_date', y='3er Schnitt', color='Spieler', markers=True, 
                   hover_data={"Datum": True, "play_date": False})
fig_line.update_traces(line=dict(width=3), marker=dict(size=8))
fig_line.update_xaxes(title="Datum", tickformat="%d.%m.%Y")
# Mobile-Optimierung: Legende horizontal über dem Chart platzieren
fig_line.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=""))
st.plotly_chart(fig_line, use_container_width=True)

st.subheader("🎯 Konstanz-Analyse")
fig_box = px.box(df_filtered, x='Spieler', y='3er Schnitt', color='Spieler', 
                 hover_data={"Datum": True})
# Mobile-Optimierung: Legende ausblenden (da die x-Achse die Spieler eh anzeigt) um Platz zu sparen
fig_box.update_layout(showlegend=False)
st.plotly_chart(fig_box, use_container_width=True)
