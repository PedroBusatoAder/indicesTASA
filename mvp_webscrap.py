import os
import json
import pandas as pd
import requests as req
from bs4 import BeautifulSoup
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === SCRAPING ===
url = "https://www.bna.com.ar/Personas"
req_response = req.get(url)

if req_response.status_code == 200:
    soup = BeautifulSoup(req_response.content, "html.parser")
    for tr_element in soup.find_all("tr"):
        if tr_element.td and "Dolar U.S.A" in tr_element.td.text:
            moneda_compra_venta = tr_element.find_all("td", limit=3)
            dolar_dic = {
                "moneda": moneda_compra_venta[0].text.strip(),
                "compra": moneda_compra_venta[1].text.strip(), #.replace(',', '.'),
                "venta": moneda_compra_venta[2].text.strip()  #.replace(',', '.')
            }
            break
else:
    raise Exception("Error al hacer scraping")

# === CONEXIÓN CON GOOGLE SHEETS ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Carga las credenciales desde variable de entorno GOOGLE_CREDENTIALS
credenciales_json = os.environ["GOOGLE_CREDENTIALS"]
credenciales_dict = json.loads(credenciales_json)
credenciales = ServiceAccountCredentials.from_json_keyfile_dict(credenciales_dict, scope)

# Autorizamos cliente gspread
gc = gspread.authorize(credenciales)

# Abrimos la hoja de cálculo usando gc (no cliente)
spreadsheet = gc.open_by_key("1jio09_eyPVeRk5ass-YV8eBouMIjLY8PTDAUq9xu-ts")
hoja = spreadsheet.worksheet("Scrap")

# Buscamos la primera fila vacía en la columna F (6)
fila = 3  # asumiendo fila 1 encabezado, fila 2 posiblemente títulos
while hoja.cell(fila, 6).value:
    fila += 1

# Actualizamos las celdas de la fila encontrada
fecha = datetime.now().strftime("%Y-%m-%d")
hoja.update_cell(fila, 6, fecha)               # F - Fecha
hoja.update_cell(fila, 7, dolar_dic["venta"])  # G - Venta
hoja.update_cell(fila, 10, dolar_dic["compra"]) # J - Compra
