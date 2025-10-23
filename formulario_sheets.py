# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 13:04:07 2025

@author: rccorreall
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Configuración de página y fondo negro
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

# Logo (opcional)
st.image("logo.png", width=300)
st.title("🧠 Encuesta de Innovación - BEPENSA")

# Conexión a Google Sheets
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["google_service_account"], scopes=scope)
client = gspread.authorize(creds)
sheet = client.open("Encuesta Innovación").sheet1

# Preguntas
preguntas = [
    "¿El equipo comunica con claridad los objetivos, la problemática que atiende y la propuesta de valor del proyecto?",
    "¿La presentación demuestra con datos y métricas concretas el impacto alcanzado o esperado del proyecto?",
    "¿El proyecto propone ideas innovadoras y se alinea con los pilares de GROWTH (Global, Rebalance, Our People, Value, The Coca-Cola Company)?",
    "¿El proyecto demuestra ser factible con los recursos disponibles y presenta un plan realista para su continuidad o expansión?",
    "¿Se evidencia un trabajo colaborativo entre distintas áreas y un impacto positivo en las personas o cultura organizacional?",
]

# Estado de envío
if "submitted" not in st.session_state:
    st.session_state.submitted = False

if not st.session_state.submitted:
    st.markdown("Selecciona una calificación del **1 al 5** para cada pregunta:")
    respuestas = []
    for i, pregunta in enumerate(preguntas):
        valor = st.radio(f"{i+1}. {pregunta}", [1,2,3,4,5], horizontal=True, key=f"p{i+1}")
        respuestas.append(valor)

    if st.button("Enviar respuesta ✅"):
        sheet.append_row([datetime.now()] + respuestas)
        st.session_state.submitted = True
        st.success("🎉 ¡Gracias por tu respuesta!")
else:
    st.success("🎉 ¡Gracias por tu respuesta!")
