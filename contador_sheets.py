# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 13:04:35 2025

@author: rccorreall
"""
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import ssl
import time

# === Config página / estilo ===
st.set_page_config(page_title="Contador BEPENSA", layout="centered")
st.markdown(
    """
    <style>
    body {background-color: black; color: white;}
    .stApp {background-color: black;}
    h1, h2, h3, label, p, div, span {color: white !important;}
    </style>
    """, unsafe_allow_html=True
)

# Logo (opcional)
try:
    st.image("logo.png", width=350)
except:
    pass

st.title("🧮 Respuestas recibidas")

# === SSL BYPASS (para entornos con certificados self-signed) ===
ssl._create_default_https_context = ssl._create_unverified_context

# === Conexión a Google Sheets ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SHEET_NAME = "Encuesta_innovacion"
WORKSHEET_NAME = "Hoja 1"

try:
    creds = Credentials.from_service_account_info(st.secrets["google_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open(SHEET_NAME)
    sheet = spreadsheet.worksheet(WORKSHEET_NAME)
except Exception as e:
    st.error("Error conectando a Google Sheets. Revisa service account, permisos y nombre de hoja.")
    st.stop()

# Placeholder grande para el contador
counter_placeholder = st.empty()

# Loop de actualización en vivo (seguro)
REFRESH_SECONDS = 2
while True:
    try:
        # get_all_values trae todas las filas; restamos 1 si hay encabezado (si no hay, quedará -1 -> max 0)
        all_values = sheet.get_all_values()
        total = max(len(all_values) - 1, 0)
    except Exception:
        total = 0

    counter_placeholder.markdown(
        f"<div style='text-align:center; margin-top:40px;'>"
        f"<h1 style='font-size:140px; color:#E63946; margin:0'>{total}</h1>"
        f"<h3 style='color:white; margin:0'>Respuestas registradas</h3>"
        f"</div>",
        unsafe_allow_html=True
    )

    time.sleep(REFRESH_SECONDS)
    # Nota: evitamos st.experimental_rerun para mantener el bucle y actualización en el mismo script

