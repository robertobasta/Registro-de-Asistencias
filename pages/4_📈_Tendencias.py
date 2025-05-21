import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression

# Configuración de la página
st.set_page_config(page_title='📈 Tendencias y Predicciones', page_icon='📊', layout='wide')
st.title("📈 Tendencias y Predicciones")

# Ruta de la base de datos
DB_ASISTENCIAS_PATH = "data/asistencias.db"

# Conectar a la base de datos
conn = sqlite3.connect(DB_ASISTENCIAS_PATH)

# Consulta de asistencias por mes desde tabla asistencias
query = '''
    SELECT strftime('%Y-%m', Fecha) as mes, COUNT(*) as asistencias
    FROM asistencias
    GROUP BY mes
    ORDER BY mes
'''
data = pd.read_sql(query, conn)

# Consulta de tabla asistencias_mensuales
query_mensual = '''
    SELECT mes, total_asistencias FROM asistencias_mensuales
'''
data_mensual = pd.read_sql(query_mensual, conn)
conn.close()

# Mapeo de meses en español
meses_mapping = {
    "Enero": "01", "Febrero": "02", "Marzo": "03", "Abril": "04",
    "Mayo": "05", "Junio": "06", "Julio": "07", "Agosto": "08",
    "Septiembre": "09", "Octubre": "10", "Noviembre": "11", "Diciembre": "12"
}

# Formateo de tabla manual
data_mensual['mes'] = data_mensual['mes'].map(lambda x: f"2024-{meses_mapping.get(x, '01')}")
data_mensual['total_asistencias'] = data_mensual['total_asistencias'].astype(int)

# Convertir a datetime
data['mes'] = pd.to_datetime(data['mes'], format='%Y-%m')
data_mensual['mes'] = pd.to_datetime(data_mensual['mes'], format='%Y-%m')

# Crear etiquetas tipo 'Enero 2024'
data['mes_etiqueta'] = data['mes'].dt.strftime('%B %Y')
data_mensual['mes_etiqueta'] = data_mensual['mes'].dt.strftime('%B %Y')

# Agregar columna fuente
data['Fuente'] = 'Histórico de la Base de Datos'
data_mensual['Fuente'] = 'Datos Manuales'

# Unir ambos datasets
data_combinada = pd.concat([data.rename(columns={'asistencias': 'total_asistencias'}), data_mensual])

# Ordenar, numerar meses y reindexar
data_combinada = data_combinada.sort_values('mes')
data_combinada['mes_num'] = np.arange(len(data_combinada))

# Agrupar mensualmente asegurando continuidad
data_combinada = data_combinada.set_index('mes').resample('M').sum().reset_index()
data_combinada['mes_etiqueta'] = data_combinada['mes'].dt.strftime('%B %Y')

# 📊 Comparación de Datos Manuales e Históricos
st.subheader("📊 Comparación de Datos de Asistencias")
fig_comparacion = px.line(data_combinada, x='mes_etiqueta', y='total_asistencias', color='Fuente',
                          markers=True, title="Comparación entre Datos Manuales y Datos de la Base de Datos")
fig_comparacion.update_xaxes(type='category')
st.plotly_chart(fig_comparacion, use_container_width=True)

# 📊 Evolución de Asistencias Mensuales
st.subheader("📊 Evolución de Asistencias Mensuales")
fig = px.line(data_combinada, x='mes_etiqueta', y='total_asistencias', markers=True,
              title="Tendencia histórica de asistencias")
fig.update_xaxes(type='category')
st.plotly_chart(fig, use_container_width=True)

# 📉 Variación Real Mensual (solo datos reales)
st.subheader("📉 Variación Real de Asistencias respecto al Mes Anterior (Base de Datos)")

# Crear copia del DataFrame real
data_real = data[['mes', 'asistencias']].copy()
data_real = data_real.sort_values('mes')
data_real['variacion'] = data_real['asistencias'].pct_change() * 100
data_real['color'] = data_real['variacion'].apply(lambda x: 'green' if x > 0 else ('red' if x < 0 else 'gray'))
data_real['variacion_label'] = data_real['variacion'].apply(lambda x: f"{x:.1f}%" if pd.notnull(x) else "")
data_real['mes_etiqueta'] = data_real['mes'].dt.strftime('%B %Y')

# Gráfica de barras
# Ordenar explícitamente por fecha
data_real = data_real.sort_values('mes')
orden_meses = data_real['mes_etiqueta'].tolist()

fig_var_real = px.bar(
    data_real,
    x='mes_etiqueta',
    y='variacion',
    color='color',
    text='variacion_label',
    title="Variación porcentual mensual real de asistencias (sin datos manuales ni predicciones)",
    category_orders={'mes_etiqueta': orden_meses},
    color_discrete_map={
    'green': '#39FF14',  # Verde fosforescente
    'red': '#FF3131',    # Rojo brillante
    'gray': '#CCCCCC'    # Gris claro para sin cambio
}
)

fig_var_real.update_layout(showlegend=False, yaxis_title="% de cambio")
fig_var_real.update_traces(textposition='outside')
fig_var_real.update_xaxes(type='category')
st.plotly_chart(fig_var_real, use_container_width=True)

# 📉 Relación entre Asistencias y Mes con línea de tendencia
st.subheader("📉 Relación entre Asistencias y Mes con Línea de Tendencia")
fig_scatter = px.scatter(data_combinada, x='mes_num', y='total_asistencias', trendline="ols", 
                         title="Relación entre Mes y Asistencias")
fig_scatter.update_layout(
    xaxis_title="Mes en Secuencia (0 = Primer Mes)",
    yaxis_title="Cantidad de Asistencias"
)
st.plotly_chart(fig_scatter, use_container_width=True)

# 📅 Comparación de asistencia por días de la semana
st.subheader("📅 Comparación de Asistencia por Día de la Semana")
dias_query = '''
    SELECT strftime('%w', Fecha) as dia, COUNT(*) as asistencias
    FROM asistencias
    GROUP BY dia
'''
conn = sqlite3.connect(DB_ASISTENCIAS_PATH)
dias_data = pd.read_sql(dias_query, conn)
conn.close()

dias_labels = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
dias_data['dia'] = dias_data['dia'].astype(int)
dias_data['dia'] = dias_data['dia'].map(lambda x: dias_labels[x])
fig_dias = px.bar(dias_data, x='dia', y='asistencias', title="Asistencia por día de la semana")
st.plotly_chart(fig_dias, use_container_width=True)

# 🔮 Predicción de asistencias futuras
st.subheader("🔮 Predicción de Asistencias para los Próximos Meses")
X = data_combinada[['mes_num']]
y = data_combinada['total_asistencias']
model = LinearRegression()
model.fit(X, y)
predicciones = model.predict([[len(data_combinada) + i] for i in range(1, 4)])

# Crear DataFrame de predicciones
pred_df = pd.DataFrame({
    'mes': [data_combinada['mes'].max() + pd.DateOffset(months=i) for i in range(1, 4)],
    'total_asistencias': predicciones
})
pred_df['mes_etiqueta'] = pred_df['mes'].dt.strftime('%B %Y')

# Concatenar para la gráfica de predicción
pred_chart_df = pd.concat([
    data_combinada[['mes_etiqueta', 'total_asistencias']],
    pred_df[['mes_etiqueta', 'total_asistencias']]
])

fig_pred = px.line(pred_chart_df, x='mes_etiqueta', y='total_asistencias', markers=True,
                   title="Predicción de asistencia futura")
fig_pred.update_xaxes(type='category')
st.plotly_chart(fig_pred, use_container_width=True)