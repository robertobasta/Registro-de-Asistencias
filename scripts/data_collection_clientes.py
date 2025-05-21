import sqlite3
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuración de Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDENTIALS_FILE = "/Users/robertobastarracheamedina/Desktop/MBW STUFF/CODIGO MBW/AsistenciasREGISTRO/asistencias-438722-408d765504fb.json"
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/14G5AdUCB1fpX6B8ztFWf58QMfdk4_d-XHdvr9w9oToE/edit?gid=393939798#gid=393939798"
SHEET_NAME = "DATOS"

def obtener_datos_google_sheets():
    """Obtiene los datos de Google Sheets y los convierte en un DataFrame."""
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
        client = gspread.authorize(creds)
        sheet = client.open_by_url(SPREADSHEET_URL).worksheet(SHEET_NAME)
        
        # Obtener todos los valores incluyendo la fila de encabezados
        data = sheet.get_all_values()
        
        # Limpiar encabezados eliminando espacios y normalizando el texto
        headers = [header.strip().upper() for header in data[0]]
        data_rows = data[1:]

        # Convertir los datos a DataFrame usando los encabezados limpios
        df = pd.DataFrame(data_rows, columns=headers)

        # Mapeo de nombres de columnas sin tildes a los nombres esperados
        column_mapping = {
            "NUMERO DE TELEFONO": "NÚMERO DE TELÉFONO",
            "CORREO ELECTRONICO": "CORREO ELECTRÓNICO",
            "GENERO": "GÉNERO"
        }
        df.rename(columns=column_mapping, inplace=True)

        # Validar si tiene las columnas esperadas
        columnas_requeridas = {"ESTATUS", "TIPO DE PLAN", "NOMBRE DEL CLIENTE", "NÚMERO DE TELÉFONO",
                               "FECHA DE CORTE", "CORREO ELECTRÓNICO", "FECHA DE NACIMIENTO", "GÉNERO"}
        if not columnas_requeridas.issubset(df.columns):
            raise ValueError(f"Faltan columnas en Google Sheets. Columnas actuales: {df.columns.tolist()}")

        return df
    except Exception as e:
        print(f"Error al obtener datos de Google Sheets: {e}")
        return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error

# Conectar a la base de datos
def get_connection():
    """Establece conexión con la base de datos SQLite."""
    try:
        return sqlite3.connect("/Users/robertobastarracheamedina/Desktop/MBW STUFF/CODIGO MBW/Registro de Asistencias/data/clientes_mbw.db", check_same_thread=False)
    except sqlite3.Error as e:
        print(f"Error al conectar con SQLite: {e}")
        return None

# Crear base de datos y tabla si no existe
def create_database():
    """Crea la tabla 'clientes' en la base de datos si no existe."""
    conn = get_connection()
    if conn is None:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estatus TEXT,
                tipo_plan TEXT,
                nombre TEXT UNIQUE,
                telefono TEXT,
                fecha_corte TEXT,
                correo TEXT,
                fecha_nacimiento TEXT,
                genero TEXT
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error al crear la tabla: {e}")
    finally:
        conn.close()

# **Actualizar toda la base de datos, no solo agregar nuevos registros**
def actualizar_clientes():
    """Elimina todos los registros en la tabla 'clientes' y carga los nuevos datos desde Google Sheets."""
    conn = get_connection()
    if conn is None:
        return
    
    df = obtener_datos_google_sheets()
    if df.empty:
        print("No se actualizaron datos porque el DataFrame está vacío.")
        return
    
    try:
        cursor = conn.cursor()

        # **1. Borrar todos los datos existentes**
        cursor.execute("DELETE FROM clientes;")
        conn.commit()  # Confirmamos la eliminación antes de insertar los nuevos datos

        # **2. Insertar los nuevos datos con REPLACE INTO**
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT OR REPLACE INTO clientes (estatus, tipo_plan, nombre, telefono, fecha_corte, correo, fecha_nacimiento, genero)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (row['ESTATUS'], row['TIPO DE PLAN'], row['NOMBRE DEL CLIENTE'], row['NÚMERO DE TELÉFONO'],
                  row['FECHA DE CORTE'], row['CORREO ELECTRÓNICO'], row['FECHA DE NACIMIENTO'], row['GÉNERO']))
        
        conn.commit()
        print("Base de datos de clientes sobrescrita con datos actualizados desde Google Sheets.")
    except sqlite3.Error as e:
        print(f"Error al actualizar la base de datos: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_database()  # Asegurar que la tabla existe
    actualizar_clientes()  # Actualizar la base de datos