import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.title("📊 Análisis de Edades de los Asistentes")

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
query_clientes = "SELECT estatus, tipo_plan, nombre, fecha_nacimiento FROM clientes"
clientes_df = pd.read_sql(query_clientes, conn_clientes)
conn_clientes.close()

# **Calcular la edad de los asistentes**
clientes_df['fecha_nacimiento'] = pd.to_datetime(clientes_df['fecha_nacimiento'], errors='coerce')
clientes_df['edad'] = clientes_df['fecha_nacimiento'].apply(lambda x: pd.Timestamp.now().year - x.year if pd.notnull(x) else None)

# **Unir datos de asistenci0'as con clientes**
df = pd.merge(asistencias_df, clientes_df, left_on="Nombre del Alumno", right_on="nombre", how="inner")
df['Fecha'] = pd.to_datetime(df['Fecha'])
df['Mes'] = df['Fecha'].dt.strftime('%Y-%m')
df['Dia'] = df['Fecha'].dt.strftime('%d')

# **📅 Asistencias por Mes (Promedio por Día y Rango de Edad)**
st.subheader("📅 Asistencias Promedio por Mes y Rango de Edad")
df['rango_edad'] = pd.cut(df['edad'], bins=[0, 18, 30, 45, 60, 100],
                           labels=['0-18', '19-30', '31-45', '46-60', '60+'])
edad_mes_df = df.groupby(['Mes', 'rango_edad'])['Nombre del Alumno'].count().reset_index()
edad_mes_df['Asistencias Promedio por Día'] = edad_mes_df['Nombre del Alumno'] / df['Dia'].nunique()
edad_mes_df.columns = ['Mes', 'Rango de Edad', 'Asistencias', 'Asistencias Promedio por Día']

fig_edad_mes = px.bar(edad_mes_df, x='Mes', y='Asistencias Promedio por Día', color='Rango de Edad',
                      title='Asistencias Promedio por Día en Cada Mes (Dividido por Rango de Edad)',
                      labels={'Rango de Edad': 'Rango de Edad', 'Asistencias Promedio por Día': 'Promedio Diario'},
                      barmode='stack')
st.plotly_chart(fig_edad_mes, use_container_width=True)

# **⏰ Promedio de Edad por Horario**
st.subheader("⏰ Promedio de Edad por Horario")
edad_horario_df = df.groupby('Horario')['edad'].mean().reset_index()
edad_horario_df.columns = ['Horario', 'Edad Promedio']

fig_edad_horario = px.bar(edad_horario_df, x='Horario', y='Edad Promedio',
                           title='Promedio de Edad por Horario',
                           labels={'Horario': 'Horario', 'Edad Promedio': 'Edad Promedio'})
st.plotly_chart(fig_edad_horario, use_container_width=True)

# **👨‍🏫 Diversidad de Edades por Coach**
st.subheader("👨‍🏫 Diversidad de Edades por Coach (Barras Apiladas)")
edad_coach_df = df.groupby(['Coaches', 'rango_edad'])['Nombre del Alumno'].count().reset_index()
edad_coach_df.columns = ['Coach', 'Rango de Edad', 'Asistencias']

fig_edad_coach = px.bar(edad_coach_df, x='Coach', y='Asistencias', color='Rango de Edad',
                         title='Asistencias por Rango de Edad y Coach',
                         labels={'Rango de Edad': 'Rango de Edad', 'Asistencias': 'Número de Asistencias'},
                         barmode='stack')
st.plotly_chart(fig_edad_coach, use_container_width=True)

# **📊 Análisis de Rango de Edades**
st.subheader("📊 Análisis de Rango de Edades")
rango_edad_df = df['rango_edad'].value_counts().reset_index()
rango_edad_df.columns = ['Rango de Edad', 'Asistencias']

fig_rango_edad = px.pie(rango_edad_df, values='Asistencias', names='Rango de Edad',
                         title='Distribución de Asistencias por Rango de Edad')
st.plotly_chart(fig_rango_edad, use_container_width=True)

st.dataframe(rango_edad_df, use_container_width=True)

st.write("📌 Las nuevas gráficas muestran promedios diarios por mes, promedios de edad por horario y asistencias divididas por rango de edad y coach.")
