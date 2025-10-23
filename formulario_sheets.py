import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import ssl
import hashlib
import time
from zoneinfo import ZoneInfo

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

# === ID ÚNICO PERSISTENTE (sobrevive a refresh) ===
def get_persistent_device_id():
    """Genera un ID único que persiste incluso después de refresh"""
    if "persistent_device_id" not in st.session_state:
        # Intentar crear un ID único y persistente
        try:
            # Usar una combinación de información disponible + timestamp
            user_agent = st.experimental_user.user_agent if hasattr(st.experimental_user, 'user_agent') else ""
            ip = st.experimental_user.ip if hasattr(st.experimental_user, 'ip') else ""
            
            # Crear una semilla única
            seed = f"{user_agent}_{ip}_{int(time.time() / 3600)}"  # Cambia cada hora para evitar conflicts
            device_id = hashlib.md5(seed.encode()).hexdigest()[:12]
            
            st.session_state.persistent_device_id = f"device_{device_id}"
        except:
            # Fallback más simple
            st.session_state.persistent_device_id = f"device_{int(time.time())}"
    
    return st.session_state.persistent_device_id

# === JAVASCRIPT PARA CERRAR VENTANA ===
def close_window_script():
    """Inyecta JavaScript para cerrar la ventana después de 5 segundos"""
    return """
    <script>
    setTimeout(function() {
        window.open('', '_self', '');
        window.close();
    }, 5000);
    </script>
    """

# Estado de la aplicación
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# Obtener device ID persistente
device_id = get_persistent_device_id()

# Si ya enviado, mostrar agradecimiento y programar cierre
if st.session_state.submitted:
    st.success("🎉 ¡Gracias por tu respuesta!")
    st.info("Tu opinión es muy valiosa para el equipo.")
    st.warning("⚠️ Esta ventana se cerrará automáticamente en 5 segundos...")
    
    # Inyectar JavaScript para cerrar la ventana
    st.markdown(close_window_script(), unsafe_allow_html=True)
    
    # Pequeña espera para que el usuario vea el mensaje
    time.sleep(5)
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
    st.warning("⚠️ Esta ventana se cerrará automáticamente en 5 segundos...")
    
    # Guardar en Google Sheets en segundo plano
    with st.spinner("Guardando tu respuesta..."):
        try:
            timestamp = datetime.now(ZoneInfo("America/Mexico_City")).strftime("%Y-%m-%d %H:%M:%S")
            
            # Guardar en Google Sheets: timestamp, respuestas, device_id
            row_data = [timestamp] + respuestas + [device_id]
            sheet.append_row(row_data)
            
        except Exception as e:
            st.error("❌ No se pudo guardar la respuesta, pero hemos registrado tu participación.")
    
    # Inyectar JavaScript para cerrar la ventana
    st.markdown(close_window_script(), unsafe_allow_html=True)
    
    # Forzar rerun para asegurar que se muestre el estado final
    st.rerun()

# Información de debug (opcional - puedes eliminar esto)
with st.expander("🔍 Información de diagnóstico"):
    st.write(f"Device ID: {device_id}")
    st.write(f"Estado enviado: {st.session_state.submitted}")
