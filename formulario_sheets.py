# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 13:04:07 2025

@author: rccorreall
"""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import ssl
import time

# === Config página / estilo ===
st.set_page_config(page_title="Encuesta BEPENSA", layout="centered")
st.markdown(
    """
    <style>
    body {background-color: black; color: white;}
    .stApp {background-color: black;}
    h1, h2, h3, label, p, div, span {color: white !important;}
    .stButton > button {background-color:#E63946;color:white;font-weight:bold;border-radius:10px;}
    </style>
    """, unsafe_allow_html=True
)

# Logo (opcional - pon logo.png en el repo)
try:
    st.image("logo.png", width=140)
except:
    pass

st.title("🧠 Encuesta de Innovación - BEPENSA")
st.write("Selecciona una calificación del **1 al 5** para cada pregunta:")

# === SSL BYPASS (para entornos con certificados self-signed) ===
# WARNING: esto evita la verificación de certificados; usar solo si es necesario en tu red.
ssl._create_default_https_context = ssl._create_unverified_context

# === Conexión a Google Sheets usando service account desde st.secrets ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = None
client = None
sheet = None
SHEET_NAME = "Encuesta_innovacion"
WORKSHEET_NAME = "Hoja 1"   # usa el nombre exacto de la pestaña

try:
    creds = Credentials.from_service_account_info(st.secrets["google_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open(SHEET_NAME)
    sheet = spreadsheet.worksheet(WORKSHEET_NAME)
except Exception as e:
    st.error("Error conectando a Google Sheets. Revisa service account, permisos y nombre de hoja.")
    st.stop()

# === Preguntas ===
preguntas = [
    "¿El equipo comunica con claridad los objetivos, la problemática que atiende y la propuesta de valor del proyecto?",
    "¿La presentación demuestra con datos y métricas concretas el impacto alcanzado o esperado del proyecto?",
    "¿El proyecto propone ideas innovadoras y se alinea con los pilares de GROWTH (Global, Rebalance, Our People, Value, The Coca-Cola Company)?",
    "¿El proyecto demuestra ser factible con los recursos disponibles y presenta un plan realista para su continuidad o expansión?",
    "¿Se evidencia un trabajo colaborativo entre distintas áreas y un impacto positivo en las personas o cultura organizacional?"
]

# Estado para evitar reenvío
if "submitted" not in st.session_state:
    st.session_state.submitted = False

if not st.session_state.submitted:
    # Mostrar cada pregunta con radio horizontal
    respuestas = []
    for i, q in enumerate(preguntas, start=1):
        r = st.radio(f"{i}. {q}", options=[1, 2, 3, 4, 5], index=2, horizontal=True, key=f"p{i}")
        respuestas.append(r)

    if st.button("Enviar respuesta ✅", use_container_width=True):
        # Guardar en Google Sheets (agregar timestamp + respuestas)
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([timestamp] + respuestas)
            st.session_state.submitted = True
            st.success("🎉 ¡Gracias por tu respuesta!")
        except Exception as e:
            st.error("No se pudo guardar la respuesta. Revisa permisos y conexión.")
            st.write(e)
else:
    st.success("🎉 ¡Gracias por tu respuesta!")
    st.info("Tu opinión es muy valiosa para el equipo.")

