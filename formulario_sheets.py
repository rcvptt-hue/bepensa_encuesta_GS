import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import ssl

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

# Logo (opcional)
try:
    st.image("logo.png", width=120)
except:
    pass

st.title("🧠 Encuesta de Innovación - BEPENSA")

# SSL BYPASS (solo si tu red lo requiere)
ssl._create_default_https_context = ssl._create_unverified_context

# Conexión a Google Sheets (st.secrets debe contener google_service_account)
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

# Preguntas
preguntas = [
    "¿El equipo comunica con claridad los objetivos, la problemática que atiende y la propuesta de valor del proyecto?",
    "¿La presentación demuestra con datos y métricas concretas el impacto alcanzado o esperado del proyecto?",
    "¿El proyecto propone ideas innovadoras y se alinea con los pilares de GROWTH (Global, Rebalance, Our People, Value, The Coca-Cola Company)?",
    "¿El proyecto demuestra ser factible con los recursos disponibles y presenta un plan realista para su continuidad o expansión?",
    "¿Se evidencia un trabajo colaborativo entre distintas áreas y un impacto positivo en las personas o cultura organizacional?"
]

# Estado para controlar envío único por sesión
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# Si ya enviado, mostrar agradecimiento
if st.session_state.submitted:
    st.success("🎉 ¡Gracias por tu respuesta!")
    st.info("Tu opinión es muy valiosa para el equipo.")
    st.stop()

# Si no enviado, mostrar el formulario (atomic submit)
with st.form("encuesta_form", clear_on_submit=False):
    st.markdown("Selecciona una calificación del **1 al 5** para cada pregunta:")
    respuestas = []
    for i, q in enumerate(preguntas, start=1):
        # keys únicas
        r = st.radio(f"{i}. {q}", options=[1,2,3,4,5], index=2, horizontal=True, key=f"radio_{i}")
        respuestas.append(r)

    submit_btn = st.form_submit_button("Enviar respuesta ✅")

# Cuando se pulsa el botón del form: marcar submitted INMEDIATAMENTE y luego intentar guardar
if submit_btn:
    # marcar para que en el siguiente render (inmediato) se oculte el formulario
    st.session_state.submitted = True

    # Mostrar spinner mientras se guarda; si falla, revertimos el estado y mostramos error
    with st.spinner("Guardando tu respuesta..."):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # append_row es la llamada a la API; puede tardar
            sheet.append_row([timestamp] + respuestas)
            # éxito: el mensaje de agradecimiento se mostrará (estado ya True)
            st.success("🎉 ¡Gracias por tu respuesta!")
        except Exception as e:
            # revertir estado para permitir reintento
            st.session_state.submitted = False
            st.error("No se pudo guardar la respuesta. Por favor intenta de nuevo.")
            st.write(f"Detalle técnico: {e}")
