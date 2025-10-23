import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import ssl
import hashlib
import uuid

# === Config página / estilo ===
st.set_page_config(page_title="Encuesta BEPENSA", layout="centered")
st.markdown(
    """
    <style>
    body {background-color: black; color: white;}
    .stApp {background-color: black;}
    h1, h2, h3, label, p, div, span {color: white !important;}
    
    .stButton > button {
        background-color: #E63946 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 10px 24px !important;
        font-size: 16px !important;
    }
    
    .stButton > button:hover {
        background-color: #D32F2F !important;
        color: white !important;
    }
    
    .stRadio > div {
        background-color: #1E1E1E;
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True
)

# Logo (opcional)
try:
    st.image("logo.png", width=350)
except:
    pass

st.title("🧠 Encuesta de Innovación - BEPENSA")

# SSL BYPASS
ssl._create_default_https_context = ssl._create_unverified_context

# Conexión a Google Sheets
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

# === ALTERNATIVAS PARA GENERAR DEVICE ID ===

def get_device_id_cookie():
    """Genera un ID único usando cookies del navegador"""
    if "device_id" not in st.session_state:
        # Intentar recuperar de cookies usando un método alternativo
        try:
            # Usamos el user agent + timestamp como fallback
            user_agent = st.experimental_user.user_agent if hasattr(st.experimental_user, 'user_agent') else "unknown"
            unique_string = f"{user_agent}_{datetime.now().timestamp()}"
            device_id = hashlib.md5(unique_string.encode()).hexdigest()
            st.session_state.device_id = device_id
        except:
            # Último recurso: UUID aleatorio
            st.session_state.device_id = str(uuid.uuid4())
    
    return st.session_state.device_id

def get_device_id_fingerprint():
    """Genera un ID basado en múltiples factores del navegador"""
    try:
        # Combinar múltiples fuentes para crear una huella digital
        user_agent = st.experimental_user.user_agent if hasattr(st.experimental_user, 'user_agent') else "unknown"
        # Agregar información de timezone y otros datos disponibles
        timestamp = str(datetime.now().timestamp())
        
        fingerprint_string = f"{user_agent}_{timestamp}"
        device_id = hashlib.sha256(fingerprint_string.encode()).hexdigest()
        return device_id
    except:
        return str(uuid.uuid4())

def get_device_id_simple():
    """Método más simple usando solo UUID"""
    if "device_id" not in st.session_state:
        st.session_state.device_id = str(uuid.uuid4())
    return st.session_state.device_id

# Estado de la aplicación
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# Usar el método simple (recomendado)
device_id = get_device_id_simple()

# Si ya enviado, mostrar agradecimiento inmediatamente
if st.session_state.submitted:
    st.success("🎉 ¡Gracias por tu respuesta!")
    st.info("Tu opinión es muy valiosa para el equipo.")
    st.stop()

# Mostrar el formulario
st.markdown("Selecciona una calificación del **1 al 5** para cada pregunta:")

# Formulario sin clear_on_submit
with st.form("encuesta_form"):
    respuestas = []
    for i, q in enumerate(preguntas, start=1):
        r = st.radio(
            f"{i}. {q}", 
            options=[1, 2, 3, 4, 5], 
            index=2, 
            horizontal=True, 
            key=f"radio_{i}"
        )
        respuestas.append(r)

    submit_btn = st.form_submit_button(
        "Enviar respuesta ✅",
        use_container_width=True
    )

# Procesar envío del formulario
if submit_btn:
    # Marcar como enviado INMEDIATAMENTE
    st.session_state.submitted = True
    
    # Mostrar mensaje de agradecimiento inmediatamente
    st.success("🎉 ¡Gracias por tu respuesta!")
    st.info("Tu opinión es muy valiosa para el equipo.")
    
    # Guardar en Google Sheets en segundo plano
    with st.spinner("Guardando tu respuesta..."):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Guardar en Google Sheets: timestamp, respuestas, device_id
            row_data = [timestamp] + respuestas + [device_id]
            sheet.append_row(row_data)
            
        except Exception as e:
            st.error("❌ No se pudo guardar la respuesta, pero hemos registrado tu participación.")
    
    # Pequeña pausa para que el usuario vea el mensaje antes del rerun
    import time
    time.sleep(1)
    st.rerun()
