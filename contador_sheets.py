# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 13:04:35 2025

@author: rccorreall
"""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import time

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

st.image("logo.png", width=300)
st.title("🧮 Contador de respuestas")

# Google Sheets
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["google_service_account"], scopes=scope)
client = gspread.authorize(creds)
sheet = client.open("Encuesta Innovación").sheet1

# Contador en vivo
placeholder = st.empty()

while True:
    total = len(sheet.get_all_values()) - 1  # menos encabezado
    with placeholder.container():
        st.markdown(f"<h1 style='text-align:center; font-size:120px; color:#E63946;'>{total}</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center;'>Respuestas recibidas</h3>", unsafe_allow_html=True)
    time.sleep(5)
    st.experimental_rerun()
