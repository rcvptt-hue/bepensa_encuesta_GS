import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import ssl
import hashlib

# === Config página / estilo ===
st.set_page_config(page_title="Encuesta BEPENSA", layout="centered")
st.markdown(
    """
    <style>
    body {background-color: black; color: white;}
    .stApp {background-color: black;}
    h1, h2, h3, label, p, div, span {color: white !important;}
    
    /* Estilo específico para el botón de enviar */
    .stButton > button {
        background-color: #E63946 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 10px 24px !important;
        font-size: 16px !important;
    }
    
    /* Estilo cuando el botón está en hover */
    .stButton > button:hover {
        background-color: #D32F2F !important;
        color: white !important;
    }
    
    /* Estilo para los radio buttons */
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
    st.image("logo.png", width=120)
except:
    pass

st.title("🧠 Encuesta de Innovación - BEPENSA")

# SSL BYPASS (solo si tu red lo requiere)
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

# === FUNCIÓN PARA GENERAR ID ÚNICO DEL DISPOSITIVO ===
def get_device_id():
    """Genera un ID único basado en la IP del usuario y user agent"""
    try:
        # Obtener información del usuario
        user_ip = st.experimental_user.ip if hasattr(st.experimental_user, 'ip') else "unknown_ip"
        user_agent = st.experimental_user.user_agent if hasattr(st.experimental_user, 'user_agent') else "unknown_agent"
        
        # Combinar y crear hash
        device_string = f"{user_ip}_{user_agent}"
        device_id = hashlib.md5(device_string.encode()).hexdigest()
        return device_id
    except:
        # Fallback
        return "unknown_device"

# Estado de la aplicación
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "device_id" not in st.session_state:
    st.session_state.device_id = get_device_id()

# Si ya enviado, mostrar agradecimiento inmediatamente
if st.session_state.submitted:
    st.success("🎉 ¡Gracias por tu respuesta!")
    st.info("Tu opinión es muy valiosa para el equipo.")
    st.stop()

# Mostrar el formulario SIN clear_on_submit para mantener las respuestas
st.markdown("Selecciona una calificación del **1 al 5** para cada pregunta:")

# Usamos un formulario pero sin clear_on_submit para mantener las respuestas visibles
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

    # Botón de enviar
    submit_btn = st.form_submit_button(
        "Enviar respuesta ✅",
        use_container_width=True
    )

# Procesar envío del formulario
if submit_btn:
    # Marcar como enviado INMEDIATAMENTE para mostrar agradecimiento rápido
    st.session_state.submitted = True
    
    # Mostrar mensaje de agradecimiento inmediatamente
    st.success("🎉 ¡Gracias por tu respuesta!")
    st.info("Tu opinión es muy valiosa para el equipo.")
    
    # Luego, en segundo plano, guardar en Google Sheets
    with st.spinner("Guardando tu respuesta..."):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            device_id = st.session_state.device_id
            
            # Guardar en Google Sheets: timestamp, respuestas, device_id
            row_data = [timestamp] + respuestas + [device_id]
            sheet.append_row(row_data)
            
        except Exception as e:
            # Si falla, mostramos error pero mantenemos el estado de enviado
            st.error("❌ No se pudo guardar la respuesta, pero hemos registrado tu participación.")
    
    # Forzar rerun para asegurar que se muestre el estado final
    st.rerun()
