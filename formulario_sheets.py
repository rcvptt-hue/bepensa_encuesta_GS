import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import ssl

# === Configuración página / estilo ===
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
try:
    st.image("logo.png", width=350)
except:
    pass

st.title("🧠 Encuesta de Innovación - BEPENSA")

# === SSL BYPASS (para entornos con certificados self-signed) ===
ssl._create_default_https_context = ssl._create_unverified_context

# === Conexión a Google Sheets usando service account de st.secrets ===
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
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

# === Preguntas ===
preguntas = [
    "¿El equipo comunica con claridad los objetivos, la problemática que atiende y la propuesta de valor del proyecto?",
    "¿La presentación demuestra con datos y métricas concretas el impacto alcanzado o esperado del proyecto?",
    "¿El proyecto propone ideas innovadoras y se alinea con los pilares de GROWTH (Global, Rebalance, Our People, Value, The Coca-Cola Company)?",
    "¿El proyecto demuestra ser factible con los recursos disponibles y presenta un plan realista para su continuidad o expansión?",
    "¿Se evidencia un trabajo colaborativo entre distintas áreas y un impacto positivo en las personas o cultura organizacional?"
]

# === Estado para controlar si ya se envió ===
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# === Renderizar según estado ===
if st.session_state.submitted:
    st.success("🎉 ¡Gracias por tu respuesta!")
    st.info("Tu opinión es muy valiosa para el equipo.")
else:
    st.write("Selecciona una calificación del **1 al 5** para cada pregunta:")

    respuestas = []
    for i, q in enumerate(preguntas, start=1):
        # Keys únicas
        r = st.radio(f"{i}. {q}", options=[1,2,3,4,5], index=2, horizontal=True, key=f"radio_{i}")
        respuestas.append(r)

    if st.button("Enviar respuesta ✅", use_container_width=True):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.append_row([timestamp] + respuestas)
            st.session_state.submitted = True
            # La app se rerenderiza automáticamente; no se necesita experimental_rerun
        except Exception as e:
            st.error("No se pudo guardar la respuesta. Revisa permisos y conexión.")
            st.write(e)
