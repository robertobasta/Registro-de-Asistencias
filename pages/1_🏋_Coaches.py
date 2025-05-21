import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title='Análisis de Coaches', page_icon='🏋️', layout='wide')

st.title("🏋️ Análisis de Coaches")

# Conectar a la base de datos
conn = sqlite3.connect("data/asistencias.db")

# Filtros en la barra lateral
st.sidebar.header("Filtros")
años_disponibles = ["Todos"] + [2024, 2025]
año = st.sidebar.selectbox("Selecciona el Año", años_disponibles)

meses = {
    "Todos": "Todos",
    "Enero": "01", "Febrero": "02", "Marzo": "03", "Abril": "04",
    "Mayo": "05", "Junio": "06", "Julio": "07", "Agosto": "08",
    "Septiembre": "09", "Octubre": "10", "Noviembre": "11", "Diciembre": "12"
}
mes = st.sidebar.selectbox("Selecciona el Mes", list(meses.keys()))
mes_num = meses[mes]

coaches_lista = ["Todos", "Adrian", "Andrea", "Elia", "Pato", "Dany"]  # Reemplazar con nombres reales
coach_filtro = st.sidebar.selectbox("Selecciona un Coach", coaches_lista)

# Construcción dinámica de la consulta SQL
query = f"""
    SELECT Coaches, Fecha, COUNT(*) as asistencias
    FROM asistencias
    WHERE 1=1
    {f"AND strftime('%Y', Fecha) = '{año}'" if año != "Todos" else ""}
    {f"AND strftime('%m', Fecha) = '{mes_num}'" if mes != "Todos" else ""}
    {f"AND Coaches = '{coach_filtro}'" if coach_filtro != "Todos" else ""}
    GROUP BY Coaches, Fecha
"""

df = pd.read_sql(query, conn)

# Verificar si el DataFrame está vacío
df = df.dropna()
if df.empty:
    st.warning("⚠️ No hay datos disponibles para los filtros seleccionados.")
    st.stop()

# Ranking de Coaches
ranking_coaches = df.groupby("Coaches")["asistencias"].sum().reset_index().sort_values(by="asistencias", ascending=False)
st.subheader(f"🏆 Coach con más asistencias en {mes} {año}")
st.dataframe(ranking_coaches)

# Gráfica de pastel
st.subheader(f"📊 Porcentaje de asistencias por Coach en {mes} {año}")
fig_pie = px.pie(ranking_coaches, values='asistencias', names='Coaches', title='Distribución de asistencias por Coaches')
st.plotly_chart(fig_pie)

# Asistencias por día de la semana
st.subheader(f"📅 Día con más asistencias en {mes} {año}")
dias_traducidos = {
    "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
    "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
}
df['día'] = pd.to_datetime(df['Fecha']).dt.day_name().map(dias_traducidos)

asistencias_dia = df.groupby("día")["asistencias"].sum().reset_index()
fig_bar = px.bar(asistencias_dia, x='día', y='asistencias', title=f'Día con más asistencias en {mes} {año}')
st.plotly_chart(fig_bar)

# Promedio de asistencias por mes
st.subheader("📊 Tendencia de Asistencias por Mes")
query_avg = f"""
    SELECT Coaches, strftime('%Y-%m', Fecha) as mes, AVG(asistencias) as promedio_asistencias
    FROM (
        SELECT Coaches, Fecha, COUNT(*) as asistencias
        FROM asistencias
        WHERE 1=1
        {f"AND strftime('%Y', Fecha) = '{año}'" if año != "Todos" else ""}
        {f"AND Coaches = '{coach_filtro}'" if coach_filtro != "Todos" else ""}
        GROUP BY Coaches, Fecha
    )
    GROUP BY Coaches, mes
"""
df_avg = pd.read_sql(query_avg, conn)

# Verificar si el DataFrame está vacío
df_avg = df_avg.dropna()
if df_avg.empty:
    st.warning("⚠️ No hay datos disponibles para los filtros seleccionados.")
    st.stop()

# Crear gráfico de líneas para mostrar la evolución del promedio de asistencias
fig_line = px.line(df_avg, x='mes', y='promedio_asistencias', color='Coaches', markers=True, title='Tendencia de asistencias por mes')
st.plotly_chart(fig_line)

# Cerrar la conexión
conn.close()