import streamlit as st
import subprocess
import base64
import os
import sqlite3
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title='Dashboard de Asistencias MBW', page_icon='📊', layout='wide')

# Ruta absoluta de Python
PYTHON_PATH = "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3"

# Rutas de las imágenes y scripts
IMAGE_PATH = "scripts/image.png"
DATA_COLLECTION_SCRIPT = "/Users/robertobastarracheamedina/Desktop/MBW STUFF/CODIGO MBW/Registro de Asistencias/scripts/data_collection.py"
DATABASE_UPDATE_SCRIPT = "/Users/robertobastarracheamedina/Desktop/MBW STUFF/CODIGO MBW/Registro de Asistencias/scripts/database_asistencias.py"
CLIENTES_UPDATE_SCRIPT = "/Users/robertobastarracheamedina/Desktop/MBW STUFF/CODIGO MBW/Registro de Asistencias/scripts/data_collection_clientes.py"
DB_PATH = "/Users/robertobastarracheamedina/Desktop/MBW STUFF/CODIGO MBW/Registro de Asistencias/data/asistencias.db"
CLIENTES_DB_PATH = "/Users/robertobastarracheamedina/Desktop/MBW STUFF/CODIGO MBW/Registro de Asistencias/data/clientes_mbw.db"

# Configurar la imagen de fondo
def set_background(image_path):
    if not os.path.exists(image_path):
        st.error(f"❌ No se encontró la imagen en: {image_path}")
        return
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url(data:image/jpg;base64,{encoded_string});
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background(IMAGE_PATH)

st.title("📊 Dashboard de Asistencias MBW")

# Conectar con la base de datos de asistencias
conn = sqlite3.connect(DB_PATH)

# Obtener años y meses disponibles
years_query = "SELECT DISTINCT strftime('%Y', Fecha) as year FROM asistencias"
years = pd.read_sql(years_query, conn)['year'].dropna().unique().tolist()
years.sort(reverse=True)

months_dict = {
    "Enero": "01", "Febrero": "02", "Marzo": "03", "Abril": "04", "Mayo": "05", "Junio": "06",
    "Julio": "07", "Agosto": "08", "Septiembre": "09", "Octubre": "10", "Noviembre": "11", "Diciembre": "12"
}
months = list(months_dict.keys())

# Selección de mes y año
year_selected = st.sidebar.selectbox("Selecciona el Año", years, index=0)
month_selected = st.sidebar.selectbox("Selecciona el Mes", months, index=3)
month_number = months_dict[month_selected]

# Obtener datos desde la base de datos
query = f'''
    SELECT Fecha, Horario, COUNT(*) as asistencias
    FROM asistencias
    WHERE strftime('%Y', Fecha) = '{year_selected}' AND strftime('%m', Fecha) = '{month_number}'
    GROUP BY Fecha, Horario
'''
data = pd.read_sql(query, conn)

conn.close()

if not data.empty:
    st.subheader(f"📊 Asistencias por horario en {month_selected} {year_selected}")
    orden_horarios = [
        "6:00 am - 7:30 am", "7:30 am - 9:00 am", "9:00 am - 10:30 am", 
        "5:00 pm - 6:30 pm", "6:30 pm - 8:00 pm", "8:00 pm - 9:30 pm", "9:30 pm - 11:00 pm"
    ]
    if 'Horario' in data.columns:
        data['Horario'] = pd.Categorical(data['Horario'], categories=orden_horarios, ordered=True)
    else:
        st.warning("⚠️ La columna 'Horario' no se encontró en los datos. Columnas disponibles: " + ", ".join(data.columns))

    fig = px.bar(
        data, x='Fecha', y='asistencias', color='Horario',
        title=f"Asistencias por horario en {month_selected} {year_selected}",
        labels={'Fecha': 'Fecha', 'asistencias': 'Asistencias'},
        barmode='stack',
        category_orders={'Horario': orden_horarios}
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ No hay datos disponibles para este mes y año.")

st.sidebar.header("⚡ Acciones")

# Función para ejecutar scripts
def run_script(script_path):
    try:
        result = subprocess.run([PYTHON_PATH, script_path], capture_output=True, text=True)
        if result.returncode == 0:
            st.success("✅ Proceso completado exitosamente")
        else:
            st.warning("⚠️ El proceso finalizó con advertencias")
        st.text_area("Salida del script:", result.stdout)
    except Exception as e:
        st.error(f"❌ Error al ejecutar el script: {str(e)}")

if st.sidebar.button("📥 Recolectar Datos"):
    run_script(DATA_COLLECTION_SCRIPT)

if st.sidebar.button("📂 Actualizar Base de Datos"):
    run_script(DATABASE_UPDATE_SCRIPT)

if st.sidebar.button("📋 Actualizar Lista de Clientes"):
    run_script(CLIENTES_UPDATE_SCRIPT)

st.write("### Bienvenido al Dashboard de Asistencias de MBW 🏋️‍♂️📊")
st.write("Selecciona una sección desde la barra lateral para explorar los datos.")
