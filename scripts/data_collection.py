import sqlite3
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from time import sleep
import re
from datetime import datetime

# Rutas de archivos
DB_PATH = "/Users/robertobastarracheamedina/Desktop/MBW STUFF/CODIGO MBW/Registro de Asistencias/data/asistencias.db"
CSV_PATH = "/Users/robertobastarracheamedina/Desktop/MBW STUFF/CODIGO MBW/Registro de Asistencias/data/asistencias.csv"

# Asegurar que la carpeta 'data' existe
os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

# Inicializa el navegador Safari
driver = webdriver.Safari()

# Abre la página de inicio de sesión
driver.get('https://mbw.com.mx/MBW112/Sistema/Ingresar')
sleep(2)

# Encuentra los campos de usuario y contraseña
usuario_input = driver.find_element(By.NAME, 'usuario')
password_input = driver.find_element(By.NAME, 'password')

# Ingresa credenciales
usuario_input.send_keys('FCOVESBW')
password_input.send_keys('B10f')

# Iniciar sesión
login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
login_button.click()
sleep(5)

# Navega a la página de asistencias
driver.get('https://mbw.com.mx/MBW112/Sistema/MisClientes')
sleep(5)

# Espera a que el botón de "Lista de Asistencias" sea visible y clickeable
try:
    wait = WebDriverWait(driver, 10)
    lista_asistencias_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'ListaAsistencias')]"))
    )
    lista_asistencias_button.click()
    sleep(5)
except:
    print("❌ Error: No se encontró el botón de 'Lista de Asistencias'.")
    driver.quit()
    exit()

# Obtener contenido HTML
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# Extraer datos de asistencias
asistencias_div = soup.find_all('div', class_='user-panel')

# Definir horarios y entrenadores
Coaches = [
    ('6:00 am - 7:30 am', '05:30', '06:59'),
    ('7:30 am - 9:00 am', '07:00', '08:29'),
    ('9:00 am - 10:30 am', '08:30', '10:30'),
    ('4:00 pm - 5:00 pm', '15:30', '16:29'),
    ('5:00 pm - 6:30 pm', '16:30', '17:58'),
    ('6:30 pm - 8:00 pm', '17:59', '19:29'),
    ('8:00 pm - 9:30 pm', '19:30', '20:48'),
    ('9:30 pm - 11:00 pm', '20:49', '23:00')
]

instructores = {
    '6:00 am - 7:30 am': 'Andrea',
    '7:30 am - 9:00 am': 'Andrea',
    '9:00 am - 10:30 am': 'Andrea',
    '4:00 pm - 5:00 pm': 'JP',
    '5:00 pm - 6:30 pm': 'Dany',
    '6:30 pm - 8:00 pm': 'Dany',
    '8:00 pm - 9:30 pm': 'Elia',
    '9:30 pm - 11:00 pm': 'Elia'
}

# Función para convertir hora de 12h a 24h
def convertir_hora_24(hora_12h):
    try:
        return datetime.strptime(hora_12h, "%I:%M %p").strftime("%H:%M")
    except ValueError:
        return None

# Función para obtener el día de la semana correctamente formateado
def obtener_dia_semana(fecha):
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    return dias_semana[fecha.weekday()]

# Función para obtener la Semana del año sin decimales
def obtener_semana_año(fecha):
    return int(fecha.isocalendar()[1])

# Procesar asistencias
resultado_final = []
fecha_actual = datetime.now()
dia_semana_actual = obtener_dia_semana(fecha_actual)
semana_actual = obtener_semana_año(fecha_actual)

for asistencia in asistencias_div:
    nombre_socio = asistencia.find('p').text.strip()
    hora_asistencia = asistencia.find('i').next_sibling.strip()

    nombre_socio = re.sub(r' - MBW FCO MONTEJO', '', nombre_socio).strip()

    hora_asistencia_match = re.search(r'\d{1,2}:\d{2} [apm]{2}', hora_asistencia)
    if hora_asistencia_match:
        hora_asistencia = convertir_hora_24(hora_asistencia_match.group())
    else:
        continue

    horario_asignado = None
    for horario, inicio, fin in Coaches:
        if inicio <= hora_asistencia <= fin:
            horario_asignado = horario
            break
    
    if dia_semana_actual == 'Sábado':
        horario_asignado = '9:00 am - 12:00 am'

    instructor = instructores.get(horario_asignado, 'Desconocido')

    nueva_asistencia = (fecha_actual.strftime('%Y-%m-%d'), nombre_socio, horario_asignado, instructor, dia_semana_actual, semana_actual)

    resultado_final.append(nueva_asistencia)

# Cerrar navegador
driver.quit()

# Guardar datos en CSV
def guardar_en_csv():
    df_nuevo = pd.DataFrame(resultado_final, columns=['Fecha', 'Nombre del Alumno', 'Horario', 'Coaches', 'Dia de la semana', 'Semana del año'])
    
    if os.path.exists(CSV_PATH):
        df_existente = pd.read_csv(CSV_PATH, encoding="utf-8")
        df_final = pd.concat([df_existente, df_nuevo], ignore_index=True).drop_duplicates()
    else:
        df_final = df_nuevo

    df_final.to_csv(CSV_PATH, index=False, encoding="utf-8")
    print("✅ Datos guardados en CSV correctamente.")

guardar_en_csv()
