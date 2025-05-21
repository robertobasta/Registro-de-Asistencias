import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.title("📊 Análisis de Género y Tipos de Plan")

# **Conectar a la base de datos**
DB_PATH = "/Users/robertobastarracheamedina/Desktop/MBW STUFF/CODIGO MBW/Registro de Asistencias/data/asistencias.db"
CLIENTES_DB_PATH = "/Users/robertobastarracheamedina/Desktop/MBW STUFF/CODIGO MBW/Registro de Asistencias/data/clientes_mbw.db"

# **Cargar datos de asistencias**
conn = sqlite3.connect(DB_PATH)
query_asistencias = 'SELECT Fecha, "Nombre del Alumno", Horario, Coaches FROM asistencias'
asistencias_df = pd.read_sql(query_asistencias, conn)
conn.close()

# **Cargar datos de clientes**
conn_clientes = sqlite3.connect(CLIENTES_DB_PATH)
query_clientes = "SELECT estatus, tipo_plan, nombre, genero FROM clientes"
clientes_df = pd.read_sql(query_clientes, conn_clientes)
conn_clientes.close()

# **Filtrar y Agrupar Tipos de Plan**
# Excluir clientes con 'estatus' en 'Baja' y 'tipo_plan' en 'Sin registros'
clientes_df = clientes_df[(clientes_df['estatus'] != 'Baja') | (clientes_df['tipo_plan'] != 'Sin registros')]

# Agrupar tipos de plan
def agrupar_tipo_plan(plan):
    if 'Mensualidad 2025' in plan:
        return 'Mensual 2025'
    elif 'Mensual - Cliente Antiguo 2024' in plan:
        return 'Mensual 2024'
    else:
        return plan

clientes_df['tipo_plan'] = clientes_df['tipo_plan'].apply(agrupar_tipo_plan)

# **Unir datos de asistencias con clientes**
df = pd.merge(asistencias_df, clientes_df, left_on="Nombre del Alumno", right_on="nombre", how="inner")

# **📅 Porcentaje de Hombres y Mujeres por Mes**
st.subheader("📅 Proporción de Hombres y Mujeres por Mes")
df['Fecha'] = pd.to_datetime(df['Fecha'])
df['Mes'] = df['Fecha'].dt.strftime('%Y-%m')
genero_mes_df = df.groupby(['Mes', 'genero'])['Nombre del Alumno'].count().reset_index()
total_por_mes = df.groupby('Mes')['Nombre del Alumno'].count().reset_index()
total_por_mes.columns = ['Mes', 'Total Asistencias']
genero_mes_df = pd.merge(genero_mes_df, total_por_mes, on='Mes')
genero_mes_df['Porcentaje'] = (genero_mes_df['Nombre del Alumno'] / genero_mes_df['Total Asistencias']) * 100
fig_genero_mes = px.bar(genero_mes_df, x='Mes', y='Porcentaje', color='genero',
                        title='Porcentaje de Asistencias por Género y Mes',
                        labels={'Porcentaje': 'Porcentaje de Asistencias', 'Mes': 'Mes'})
st.plotly_chart(fig_genero_mes, use_container_width=True)

# **⏰ Proporción Promedio de Hombres y Mujeres por Horario**
st.subheader("⏰ Proporción Promedio de Hombres y Mujeres por Horario")
genero_horario_df = df.groupby(['Horario', 'genero'])['Nombre del Alumno'].count().reset_index()
total_por_horario = df.groupby('Horario')['Nombre del Alumno'].count().reset_index()
total_por_horario.columns = ['Horario', 'Total Asistencias']
genero_horario_df = pd.merge(genero_horario_df, total_por_horario, on='Horario')
genero_horario_df['Porcentaje'] = (genero_horario_df['Nombre del Alumno'] / genero_horario_df['Total Asistencias']) * 100
fig_genero_horario = px.bar(genero_horario_df, x='Horario', y='Porcentaje', color='genero',
                            title='Porcentaje de Asistencias por Género y Horario',
                            labels={'Porcentaje': 'Porcentaje de Asistencias', 'Horario': 'Horario'})
st.plotly_chart(fig_genero_horario, use_container_width=True)

# **👨‍🏫 Porcentaje de Hombres y Mujeres por Coach**
st.subheader("👨‍🏫 Porcentaje de Hombres y Mujeres por Coach")
genero_coach_df = df.groupby(['Coaches', 'genero'])['Nombre del Alumno'].count().reset_index()
total_por_coach = df.groupby('Coaches')['Nombre del Alumno'].count().reset_index()
total_por_coach.columns = ['Coaches', 'Total Asistencias']
genero_coach_df = pd.merge(genero_coach_df, total_por_coach, on='Coaches')
genero_coach_df['Porcentaje'] = (genero_coach_df['Nombre del Alumno'] / genero_coach_df['Total Asistencias']) * 100
fig_genero_coach = px.bar(genero_coach_df, x='Coaches', y='Porcentaje', color='genero',
                            title='Porcentaje de Asistencias por Género y Coach',
                            labels={'Porcentaje': 'Porcentaje de Asistencias', 'Coaches': 'Coach'})
st.plotly_chart(fig_genero_coach, use_container_width=True)

# **📊 Comparación de Asistencias por Tipo de Plan y Género**
st.subheader("📊 Comparación de Asistencias por Tipo de Plan y Género")
tipo_plan_df = df.groupby(['tipo_plan', 'genero'])['Nombre del Alumno'].count().reset_index()
total_por_plan = df.groupby('tipo_plan')['Nombre del Alumno'].count().reset_index()
total_por_plan.columns = ['tipo_plan', 'Total Asistencias']
tipo_plan_df = pd.merge(tipo_plan_df, total_por_plan, on='tipo_plan')
tipo_plan_df['Porcentaje'] = (tipo_plan_df['Nombre del Alumno'] / tipo_plan_df['Total Asistencias']) * 100
fig_tipo_plan = px.bar(tipo_plan_df, x='tipo_plan', y='Porcentaje', color='genero',
                        title='Porcentaje de Asistencias por Género y Tipo de Plan',
                        labels={'Porcentaje': 'Porcentaje de Asistencias', 'tipo_plan': 'Tipo de Plan'})
st.plotly_chart(fig_tipo_plan, use_container_width=True)

st.write("📌 Este análisis permite identificar patrones en la asistencia, mostrando la proporción de hombres y mujeres por mes, horario, coach y tipo de plan, aplicando las nuevas reglas de agrupación de planes.")
