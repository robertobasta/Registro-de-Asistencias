import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.title("📊 Estatus de Asistentes por Coach")

# **Conectar a la base de datos**
DB_PATH = "/Users/robertobastarracheamedina/Desktop/MBW STUFF/CODIGO MBW/Registro de Asistencias/data/asistencias.db"
CLIENTES_DB_PATH = "/Users/robertobastarracheamedina/Desktop/MBW STUFF/CODIGO MBW/Registro de Asistencias/data/clientes_mbw.db"

# **Cargar datos de asistencias**
conn = sqlite3.connect(DB_PATH)
query_asistencias = 'SELECT DISTINCT "Nombre del Alumno", Coaches FROM asistencias'
asistencias_df = pd.read_sql(query_asistencias, conn)
conn.close()

# **Cargar datos de clientes**
conn_clientes = sqlite3.connect(CLIENTES_DB_PATH)
query_clientes = "SELECT nombre, estatus, tipo_plan FROM clientes"
clientes_df = pd.read_sql(query_clientes, conn_clientes)
conn_clientes.close()

# **Unir datos de asistencias con clientes únicos**
df = pd.merge(asistencias_df, clientes_df, left_on="Nombre del Alumno", right_on="nombre", how="inner")

# **Contar clientes únicos por coach y estatus**
estatus_coach_df = df.groupby(['Coaches', 'estatus'])['nombre'].nunique().reset_index()
estatus_coach_df.columns = ['Coach', 'Estatus', 'Número de Clientes Únicos']

# **📊 Gráfico de Clientes Únicos por Estatus y Coach**
st.subheader("📊 Clientes Únicos Activos, Sin Renovar y en Baja por Coach")
fig_estatus_coach = px.bar(estatus_coach_df, x='Coach', y='Número de Clientes Únicos', color='Estatus',
                            title='Clientes Únicos por Estatus y Coach',
                            labels={'Número de Clientes Únicos': 'Número de Clientes Únicos', 'Estatus': 'Estatus del Cliente'},
                            barmode='stack')
st.plotly_chart(fig_estatus_coach, use_container_width=True)

# **📈 Evolución del Estatus de Clientes Únicos por Coach**
st.subheader("📈 Evolución del Estatus de Clientes Únicos por Coach")
fig_evolucion = px.bar(estatus_coach_df, x='Coach', y='Número de Clientes Únicos', color='Estatus',
                         title='Tendencia de Clientes Únicos por Estatus y Coach',
                         labels={'Número de Clientes Únicos': 'Número de Clientes Únicos', 'Estatus': 'Estatus del Cliente'},
                         barmode='group')
st.plotly_chart(fig_evolucion, use_container_width=True)

# **📋 Tabla Resumida del Estatus de Clientes Únicos por Coach**
st.subheader("📋 Tabla Resumida del Estatus de Clientes Únicos por Coach")
tabla_resumida = df.pivot_table(index='Coaches', columns='estatus', values='nombre', aggfunc='nunique', fill_value=0)
st.dataframe(tabla_resumida, use_container_width=True)

st.write("📌 Esta visualización muestra el número real de clientes únicos asignados a cada coach, evitando la inflación de números por asistencias repetidas.")
