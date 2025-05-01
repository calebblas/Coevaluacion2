from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# Autenticación con Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credenciales.json', scope)
client = gspread.authorize(creds)

# Abrir la hoja
SHEET_ID = '1f2zruI_aJ7i9dgjdvekgBSgLlOaIRHN4kdO7tlYMEVY'
sheet = client.open_by_key(SHEET_ID).sheet1  # Usa la primera hoja

# Helpers para trabajar con datos
def get_all_data():
    data = sheet.get_all_records()
    return data

def extract_sections_groups(data):
    secciones = set()
    grupos_por_seccion = {}

    for row in data:
        clave = row['Sección_Grupo_Orden']
        partes = clave.split('_')
        if len(partes) != 3:
            continue
        seccion, grupo, _ = partes
        secciones.add(seccion)
        if seccion not in grupos_por_seccion:
            grupos_por_seccion[seccion] = set()
        grupos_por_seccion[seccion].add(grupo)

    return list(secciones), {k: list(v) for k, v in grupos_por_seccion.items()}

def get_estudiantes(seccion, grupo, data):
    nombres = []
    for row in data:
        clave = row['Sección_Grupo_Orden']
        partes = clave.split('_')
        if len(partes) != 3:
            continue
        sec, grp, _ = partes
        if sec == seccion and grp == grupo:
            nombres.append(row['Nombres'])
    return nombres

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def css():
    return send_from_directory('.', 'style.css')

@app.route('/script.js')
def js():
    return send_from_directory('.', 'script.js')

@app.route('/secciones')
def secciones():
    data = get_all_data()
    secciones, _ = extract_sections_groups(data)
    return jsonify(secciones)

@app.route('/grupos/<seccion>')
def grupos(seccion):
    data = get_all_data()
    _, grupos_por_seccion = extract_sections_groups(data)
    return jsonify(grupos_por_seccion.get(seccion, []))

@app.route('/nombres/<seccion>/<grupo>')
def nombres(seccion, grupo):
    data = get_all_data()
    nombres = get_estudiantes(seccion, grupo, data)
    return jsonify(nombres)

@app.route('/guardar', methods=['POST'])
def guardar():
    payload = request.json
    evaluador = payload['evaluador']
    respuestas = payload['respuestas']  # { 'Alumno 1': 2, 'Alumno 2': 3, ... }
    evaluacion_num = payload['evaluacion']  # 1, 2, 3 o 4

    data = sheet.get_all_records()
    nombres = [row['Nombres'] for row in data]

    header = sheet.row_values(1)

    for nombre_evaluado, nota in respuestas.items():
        if nombre_evaluado == evaluador:
            continue  # No guardamos autoevaluación aquí

        # Buscar fila del alumno evaluado
        fila = nombres.index(nombre_evaluado) + 2  # +2 por encabezado y 0-index

        # Buscar columna correspondiente a la evaluación
        for i, col in enumerate(header):
            if col.startswith(f'Coev {evaluacion_num}') and sheet.cell(fila, i + 1).value == '':
                sheet.update_cell(fila, i + 1, nota)
                break

    return jsonify({'mensaje': 'Datos guardados correctamente'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)