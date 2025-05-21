import sqlite3

# Conectar a la base de datos
db_path = "/Users/robertobastarracheamedina/Desktop/MBW STUFF/CODIGO MBW/Registro de Asistencias/data/asistencias.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear la tabla si no existe
cursor.execute("""
CREATE TABLE IF NOT EXISTS asistencias_mensuales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mes TEXT UNIQUE,
    total_asistencias INTEGER
)
""")

# Datos de asistencias por mes
datos_asistencias = [
    ("Enero", 853),
    ("Febrero", 1440),
    ("Marzo", 1790),
    ("Abril", 2013),
    ("Mayo", 1885),
    ("Junio", 1864)
]

# Insertar los datos (evita duplicados con INSERT OR IGNORE)
for mes, total in datos_asistencias:
    cursor.execute("INSERT OR IGNORE INTO asistencias_mensuales (mes, total_asistencias) VALUES (?, ?)", (mes, total))

# Guardar y cerrar conexión
conn.commit()
conn.close()

print("Datos insertados correctamente.")