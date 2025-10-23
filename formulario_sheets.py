import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import ssl
import hashlib
import time
from zoneinfo import ZoneInfo
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
    
    .close-message {
        background-color: #1B5E20;
        padding: 20px;
        border-radius: 10px;
        border-left: 6px solid #4CAF50;
        margin: 25px 0;
        text-align: center;
    }
    
    .close-message h3 {
        color: #4CAF50 !important;
        margin-bottom: 10px;
    }
    
    .close-message p {
        font-size: 18px;
        margin-bottom: 5px;
    }
    
    .loading-message {
        background-color: #E65100;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 15px 0;
        border-left: 5px solid #FF9800;
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

# === ID ÚNICO MEJORADO (sin mostrar al usuario) ===
def get_session_device_id():
    """Genera un ID único por sesión que persiste hasta cerrar la ventana"""
    if "session_device_id" not in st.session_state:
        # Generar un UUID único para esta sesión
        session_uuid = str(uuid.uuid4())
        
        # Crear un ID de sesión simple pero único
        session_id = f"ses_{session_uuid[:12]}"
        st.session_state.session_device_id = session_id
    
    return st.session_state.session_device_id

# Estado de la aplicación
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "processing" not in st.session_state:
    st.session_state.processing = False

# Obtener device ID de sesión (no se muestra al usuario)
device_id = get_session_device_id()

# Si ya enviado, mostrar agradecimiento
if st.session_state.submitted:
    st.success("🎉 ¡Gracias por tu respuesta!")
    st.info("Tu opinión es muy valiosa para el equipo.")
    
    # Mensaje para cerrar manualmente
    st.markdown(
        """
        <div class="close-message">
        <h3>🏁 ENCUESTA COMPLETADA</h3>
        <p><strong>Por favor, cierra esta ventana/pestaña de tu navegador</strong></p>
        <p>¡Gracias por tu participación!</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    st.stop()

# Mostrar el formulario
st.markdown("Selecciona una calificación del **1 al 5** para cada pregunta:")

# Formulario sin clear_on_submit para mantener las respuestas visibles
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

# Si se está procesando, mostrar mensaje de espera
if st.session_state.processing:
    st.markdown(
        """
        <div class="loading-message">
        <h3>⏳ Espera unos momentos</h3>
        <p>Estamos procesando tu respuesta...</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Procesar envío del formulario
if submit_btn and not st.session_state.processing:
    # Marcar que estamos procesando
    st.session_state.processing = True
    st.session_state.form_responses = respuestas
    
    # Forzar rerun para mostrar el mensaje de espera inmediatamente
    st.rerun()

# Este código se ejecuta después del rerun, cuando processing es True
if st.session_state.get('processing', False) and not st.session_state.get('submitted', False):
    # Recuperar las respuestas guardadas
    respuestas = st.session_state.form_responses
    
    # Guardar en Google Sheets
    with st.spinner("Guardando tu respuesta..."):
        try:
            timestamp = datetime.now(ZoneInfo("America/Mexico_City")).strftime("%Y-%m-%d %H:%M:%S")
            
            # Guardar en Google Sheets: timestamp, respuestas, device_id
            row_data = [timestamp] + respuestas + [device_id]
            sheet.append_row(row_data)
            
            # Mensaje de éxito
            st.success("✅ Respuesta guardada exitosamente")
            
        except Exception as e:
            st.error("❌ No se pudo guardar la respuesta en el sistema.")
    
    # Marcar como enviado
    st.session_state.submitted = True
    st.session_state.processing = False
    
    # Forzar rerun final para mostrar pantalla de agradecimiento
    st.rerun()
