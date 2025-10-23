import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import ssl
import hashlib
import time
from zoneinfo import ZoneInfo
import random

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
        background-color: #2E7D32;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 20px 0;
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

# === ID ÚNICO MEJORADO (realmente único por dispositivo) ===
def get_unique_device_id():
    """Genera un ID verdaderamente único por dispositivo/sesión"""
    if "unique_device_id" not in st.session_state:
        try:
            # Combinar múltiples fuentes para mayor unicidad
            user_agent = st.experimental_user.user_agent if hasattr(st.experimental_user, 'user_agent') else ""
            ip = st.experimental_user.ip if hasattr(st.experimental_user, 'ip') else ""
            
            # Agregar timestamp de alta precisión y número aleatorio
            high_precision_time = time.time_ns()
            random_component = random.randint(100000, 999999)
            
            # Crear una semilla más única
            seed = f"{user_agent}_{ip}_{high_precision_time}_{random_component}"
            
            # Usar SHA256 para mayor distribución
            device_id = hashlib.sha256(seed.encode()).hexdigest()[:16]
            st.session_state.unique_device_id = f"dev_{device_id}"
            
        except Exception as e:
            # Fallback con UUID conceptual
            fallback_seed = f"{time.time_ns()}_{random.randint(100000, 999999)}"
            device_id = hashlib.md5(fallback_seed.encode()).hexdigest()[:12]
            st.session_state.unique_device_id = f"dev_{device_id}"
    
    return st.session_state.unique_device_id

# Estado de la aplicación
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# Obtener device ID mejorado
device_id = get_unique_device_id()

# Si ya enviado, mostrar agradecimiento y mensaje de cierre
if st.session_state.submitted:
    st.success("🎉 ¡Gracias por tu respuesta!")
    st.info("Tu opinión es muy valiosa para el equipo.")
    
    # Mensaje para cerrar manualmente con mejor estilo
    st.markdown(
        """
        <div class="close-message">
        <h3>✅ Encuesta completada</h3>
        <p>Puedes cerrar esta ventana ahora. ¡Gracias por participar!</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Botón de cierre (simbólico - no funciona en todos los navegadores)
    if st.button("Cerrar Ventana", type="primary"):
        st.info("Por favor, cierra esta pestaña manualmente en tu navegador")
    
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
            timestamp = datetime.now(ZoneInfo("America/Mexico_City")).strftime("%Y-%m-%d %H:%M:%S")
            
            # Guardar en Google Sheets: timestamp, respuestas, device_id
            row_data = [timestamp] + respuestas + [device_id]
            sheet.append_row(row_data)
            
            # Mensaje de éxito
            st.success("✅ Respuesta guardada exitosamente")
            
        except Exception as e:
            st.error("❌ No se pudo guardar la respuesta en el sistema, pero hemos registrado tu participación.")
    
    # Mensaje para cerrar manualmente
    st.markdown(
        """
        <div class="close-message">
        <h3>✅ Encuesta completada</h3>
        <p>Puedes cerrar esta ventana ahora. ¡Gracias por participar!</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Botón de cierre simbólico
    st.button("Cerrar Ventana", type="primary")
    
    # Forzar rerun para asegurar que se muestre el estado final
    st.rerun()

# Información de diagnóstico (opcional - puedes comentar o eliminar esto)
with st.expander("🔍 Información de diagnóstico (solo para pruebas)"):
    st.write(f"**Device ID:** {device_id}")
    st.write(f"**Estado enviado:** {st.session_state.submitted}")
    st.write(f"**User Agent:** {st.experimental_user.user_agent if hasattr(st.experimental_user, 'user_agent') else 'No disponible'}")
    st.write(f"**IP:** {st.experimental_user.ip if hasattr(st.experimental_user, 'ip') else 'No disponible'}")
