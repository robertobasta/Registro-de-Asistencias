import sqlite3
import pandas as pd
import os
from datetime import datetime

# Rutas de archivos
DB_PATH = "/Users/robertobastarracheamedina/Desktop/MBW STUFF/CODIGO MBW/Registro de Asistencias/data/asistencias.db"
CSV_PATH = "/Users/robertobastarracheamedina/Desktop/MBW STUFF/CODIGO MBW/Registro de Asistencias/data/asistencias.csv"
FALTANTES_PATH = "/Users/robertobastarracheamedina/Desktop/MBW STUFF/CODIGO MBW/Registro de Asistencias/data/datos_faltantes.csv"

def connect_db():
    """Establece conexión con la base de datos SQLite."""
    return sqlite3.connect(DB_PATH)

def create_table():
    """Crea la tabla de asistencias si no existe."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asistencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Fecha TEXT,
            "Nombre del Alumno" TEXT,
            Horario TEXT,
            Coaches TEXT,
            "Dia de la semana" TEXT,
            "Semana del año" INTEGER
        )
    """)
    conn.commit()
    conn.close()

def convertir_fecha(fecha):
    """Convierte una fecha en formato DD/MM/YYYY a YYYY-MM-DD."""
    try:
        return datetime.strptime(fecha, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return fecha  # Si ya está en formato correcto, la devuelve sin cambios.

def load_csv_to_db():
    """Carga los datos del CSV a la base de datos, evitando duplicados y mostrando errores."""
    
    # Verificar si el archivo CSV existe
    if not os.path.exists(CSV_PATH):
        print("⚠️ No se encontró el archivo CSV, asegúrate de que existe.")
        return

    # Leer el CSV asegurando que los nombres de las columnas sean correctos
    df = pd.read_csv(CSV_PATH, encoding="utf-8")

    # Verificar que las columnas esperadas estén en el DataFrame
    columnas_esperadas = {"Fecha", "Nombre del Alumno", "Horario", "Coaches", "Dia de la semana", "Semana del año"}
    if not columnas_esperadas.issubset(set(df.columns)):
        print(f"⚠️ El CSV no contiene las columnas esperadas. Se encontraron: {df.columns.tolist()}")
        return

    # Convertir las fechas al formato correcto
    df["Fecha"] = df["Fecha"].apply(convertir_fecha)

    # Asegurar que "Semana del año" es un entero válido
    df["Semana del año"] = pd.to_numeric(df["Semana del año"], errors="coerce").fillna(0).astype(int)

    # Filtrar filas con fechas inválidas
    df_validas = df.dropna(subset=["Fecha"])

    # Filtrar las filas inválidas para reportarlas
    df_invalidas = df[df["Fecha"].isna()]

    # Conectar a la base de datos
    conn = connect_db()
    cursor = conn.cursor()

    errores = []  # Lista para almacenar errores

    # Insertar los datos evitando duplicados
    for _, row in df_validas.iterrows():
        try:
            cursor.execute("""
                INSERT INTO asistencias (Fecha, "Nombre del Alumno", Horario, Coaches, "Dia de la semana", "Semana del año")
                SELECT ?, ?, ?, ?, ?, ?
                WHERE NOT EXISTS (
                    SELECT 1 FROM asistencias 
                    WHERE Fecha = ? AND "Nombre del Alumno" = ? AND Coaches = ?
                )
            """, (row["Fecha"], row["Nombre del Alumno"], row["Horario"], row["Coaches"], 
                  row["Dia de la semana"], row["Semana del año"],
                  row["Fecha"], row["Nombre del Alumno"], row["Coaches"]))

        except Exception as e:
            errores.append(f"❌ Error con {row['Nombre del Alumno']} el {row['Fecha']}: {str(e)}")

    conn.commit()

    # ✅ Corregir el problema con `df_post_db`
    df_post_db = pd.read_sql("SELECT Fecha, \"Nombre del Alumno\", Coaches FROM asistencias", conn)

    conn.close()

    # 🔹 Identificar datos que no se insertaron
    df_faltantes = df_validas.merge(df_post_db, on=["Fecha", "Nombre del Alumno", "Coaches"], how="left", indicator=True)
    df_faltantes = df_faltantes[df_faltantes["_merge"] == "left_only"].drop(columns=["_merge"])

    print("✅ Datos del CSV cargados en la base de datos sin duplicados.")

    # Mostrar los datos que no se pasaron y por qué
    if not df_invalidas.empty or not df_faltantes.empty or errores:
        print("\n⚠️ Algunos datos no se insertaron en la base de datos:")
        
        if not df_invalidas.empty:
            print("❌ Filas con fechas inválidas:")
            print(df_invalidas[["Nombre del Alumno", "Fecha"]])

        if not df_faltantes.empty:
            print("\n❌ Registros que no se insertaron porque no pasaron la validación:")
            print(df_faltantes)

            # Guardar los registros faltantes en un CSV para análisis posterior
            df_faltantes.to_csv(FALTANTES_PATH, index=False, encoding="utf-8")
            print(f"\n📁 Se guardaron {len(df_faltantes)} registros faltantes en {FALTANTES_PATH}")

        if errores:
            print("\n❌ Errores encontrados:")
            for error in errores:
                print(error)

if __name__ == "__main__":
    create_table()
    load_csv_to_db()