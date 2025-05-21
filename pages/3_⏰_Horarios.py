import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title='Análisis de Horarios', page_icon='⏰', layout='wide')

st.title("⏰ Análisis de Horarios")

# Conectar a la base de datos
conn = sqlite3.connect("data/asistencias.db")

# Filtros en la barra lateral
st.sidebar.header("Filtros")
año = st.sidebar.selectbox("Selecciona el Año", ["Todos", 2024, 2025])
meses = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
mes = st.sidebar.selectbox("Selecciona el Mes", ["Todos"] + list(meses.values()))
mes_num = str(list(meses.keys())[list(meses.values()).index(mes)]).zfill(2) if mes != "Todos" else "Todos"

# Filtro de Horarios
orden_horarios = [
    "6:00 am - 7:30 am", "7:30 am - 9:00 am", "9:00 am - 10:30 am", 
    "5:00 pm - 6:30 pm", "6:30 pm - 8:00 pm", "8:00 pm - 9:30 pm", "9:30 pm - 11:00 pm"
]
horario_filtro = st.sidebar.selectbox("Selecciona un Horario", ["Todos"] + orden_horarios)

# Obtener datos de la base de datos
query = f"""
    SELECT Fecha, Horario, COUNT(*) as asistencias
    FROM asistencias
    WHERE 1=1
    {f"AND strftime('%Y', Fecha) = '{año}'" if año != "Todos" else ""}
    {f"AND strftime('%m', Fecha) = '{mes_num}'" if mes != "Todos" else ""}
    {f"AND Horario = '{horario_filtro}'" if horario_filtro != "Todos" else ""}
    GROUP BY Fecha, Horario
"""
df = pd.read_sql(query, conn)

# Verificar si el DataFrame está vacío
df = df.dropna()
if df.empty:
    st.warning("⚠️ No hay datos disponibles para los filtros seleccionados.")
    st.stop()

# 📊 Gráfica de Barras Apiladas
st.subheader(f"📊 Asistencias por Horario en {mes} {año}" if año != "Todos" and mes != "Todos" else "📊 Asistencias por Horario")
fig_bar = px.bar(df, x='Fecha', y='asistencias', color='Horario', title='Asistencias por horario', barmode='stack', category_orders={'Horario': orden_horarios})
st.plotly_chart(fig_bar)

# 📈 **Tendencia de Asistencias por Horario**
st.subheader("📈 Evolución del Promedio de Asistencias por Horario")

# Obtener datos de tendencia
query_tendencia = f"""
    SELECT Horario, strftime('%Y-%m', Fecha) as mes, AVG(asistencias) as promedio_asistencias
    FROM (
        SELECT Horario, Fecha, COUNT(*) as asistencias
        FROM asistencias
        WHERE 1=1
        {f"AND strftime('%Y', Fecha) = '{año}'" if año != "Todos" else ""}
        {f"AND strftime('%m', Fecha) = '{mes_num}'" if mes != "Todos" else ""}
        GROUP BY Horario, Fecha
    )
    {f"WHERE Horario = '{horario_filtro}'" if horario_filtro != "Todos" else ""}
    GROUP BY Horario, mes
"""
df_tendencia = pd.read_sql(query_tendencia, conn)

# Verificar si hay datos para mostrar
df_tendencia = df_tendencia.dropna()
if df_tendencia.empty:
    st.warning("⚠️ No hay datos disponibles para la tendencia de asistencias por horario.")
else:
    # Crear gráfico de líneas para visualizar el promedio de asistencias por horario
    fig_tendencia = px.line(df_tendencia, x='mes', y='promedio_asistencias', color='Horario', markers=True, title="Tendencia de Asistencias por Horario")
    st.plotly_chart(fig_tendencia)

# 📊 Gráfica de Áreas Apiladas
st.subheader("📊 Tendencia de Asistencias por Horario")
fig_area = px.area(df, x='Fecha', y='asistencias', color='Horario', title='Tendencia de Asistencias por Horario', category_orders={'Horario': orden_horarios})
st.plotly_chart(fig_area)

# 🔥 **Mapa de Calor**
st.subheader("🔥 Mapa de Calor de Asistencias por Horario")
fig_heatmap = px.density_heatmap(df, x='Fecha', y='Horario', z='asistencias', title='Mapa de Calor de Asistencias por Horario', color_continuous_scale='Blues')
st.plotly_chart(fig_heatmap)

# 📊 **Gráfica de Dispersión**
st.subheader("📊 Distribución de Asistencias por Horario")
fig_scatter = px.scatter(df, x='Fecha', y='Horario', size='asistencias', color='Horario', title='Distribución de Asistencias por Horario', category_orders={'Horario': orden_horarios})
st.plotly_chart(fig_scatter)

# 🔄 **Gráfica de Radar**
st.subheader("🔄 Distribución de Asistencias por Horario")
df_radar = df.groupby('Horario')['asistencias'].sum().reset_index()
fig_radar = px.line_polar(df_radar, r='asistencias', theta='Horario', line_close=True, title='Distribución de Asistencias por Horario')
st.plotly_chart(fig_radar)

# Cerrar conexión
conn.close()