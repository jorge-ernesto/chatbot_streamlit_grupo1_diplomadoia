"""
App Importante (UI): Chatbot IA - Médico Oncológico con Streamlit y Groq

Qué hace:
    Chatbot IA con historial de conversación usando Streamlit y Groq. Permite elegir desde el sidebar el área de interés oncológico
    (General, cáncer de mama, pulmón, colon, leucemia / linfoma u otro) y el idioma de respuesta (Español, English, Português).
    Construye un mensaje de sistema dinámico para restringir al asistente exclusivamente a temas de oncología,
    recordar que la información es solo orientativa y forzar el idioma seleccionado. Usa session_state para conservar
    el historial del chat, renderiza los mensajes previos, responde mediante la API de Groq y ofrece botón para iniciar
    una nueva conversación.

Tecnologías:
    Streamlit (set_page_config, title, write, sidebar, selectbox, chat_input, chat_message, button, session_state, rerun),
    Groq (cliente y chat completions), python-dotenv y os (carga de GROQ_API_KEY desde .env o secrets de Streamlit).

Ejecutar:
    cd 5 Python/2 master-python-datascience/chatbot_streamlit_grupo1_diplomadoia
    streamlit run app.py
"""

############################################################
#                    IMPORTAR LIBRERIAS                   #
############################################################

import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os

############################################################
#              CONFIGURAR VARIABLES DE ENTORNO             #
############################################################

# Cargar la API key de forma segura
try:
    load_dotenv()  # Carga variables desde .env si existe (entorno local)
    API_KEY = os.getenv("GROQ_API_KEY")  # para Groq; usar "OPENAI_API_KEY" si es OpenAI
except:
    API_KEY = st.secrets["GROQ_API_KEY"]

os.environ["GROQ_API_KEY"] = API_KEY
client = Groq()  # Cliente para invocar la API de Groq

############################################################
#                      CONFIGURAR APP                     #
############################################################

# ****************** Configurar pagina ******************

# Configurar pagina
st.set_page_config(page_title="Chatbot con IA", page_icon="🤖", layout="centered")
st.title("🏥 Chatbot IA - Médico especializado en Oncología (Demo)")
st.write("Puedes hacer preguntas y el chatbot responderá usando un modelo de lenguaje.")

# Sidebar
# Modelos Groq: https://console.groq.com/docs/models
with st.sidebar:
    st.header("Configuración")
    tipo_cancer = st.selectbox("Área de interés", [
        "General",
        "Cáncer de mama",
        "Cáncer de pulmón",
        "Cáncer de colon",
        "Leucemia / Linfoma",
        "Otro",
    ])
    idioma = st.selectbox("Idioma", [
        "Español",
        "English",
        "Português"
    ])
    
    # ****************** Crear el system prompt con comportamiento específico ******************

    SYSTEM_PROMPT = f"""
    Eres un asistente médico especializado exclusivamente en oncología.
    Preséntate siempre como médico oncólogo al inicio de cada conversación, no es necesario que digas tu nombre, tu representas el area de oncología en general, no un hospital o clínica específica.
    Responde únicamente preguntas relacionadas con oncología (tipos de cáncer, diagnóstico, tratamientos, prevención, efectos secundarios, etc.).
    Si el usuario pregunta sobre cualquier otro tema fuera de tu especialidad, declina amablemente e indica que solo puedes asistir en temas oncológicos.
    Recuerda al usuario que tus respuestas son informativas y no reemplazan una consulta médica presencial.

    Área de interés oncológico: {tipo_cancer}. Si no es 'General', prioriza información relacionada con ese tipo de cáncer.

    Responde siempre en {idioma}, sin excepción, independientemente del idioma en que escriba el usuario o el historial de mensajes que tengas.
    """
    print("SYSTEM_PROMPT", SYSTEM_PROMPT)

# ****************** Inicializar la variable "chat_history" que tendra el historial de mensajes en "session_state" ******************

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # lista de dicts: {"role": ..., "content": ...}

# ****************** Renderizar historial de mensajes ******************

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ****************** Input de usuario ******************

# chat_input: Es el widget de entrada de chat, esta pensado para ir fijo en la parte inferior de la pantalla como en WhatsApp o Telegram
user_input = st.chat_input("Escribe tu pregunta aquí...")

if user_input:
    # Mostrar el mensaje del usuario
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Construir mensajes para el modelo
    messages = []
    if SYSTEM_PROMPT:
        messages.append({"role": "system", "content": SYSTEM_PROMPT})
        messages.extend(st.session_state.chat_history)
        print("messages", messages)

        # Llamar a la API **solo** si hay user_input (evita NameError)
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # llama-3.3-70b-versatile | llama-3.1-8b-instant | openai/gpt-oss-120b | openai/gpt-oss-20b
                messages=messages,
                temperature=0.7,
            )
            respuesta_texto = response.choices[0].message.content  # objeto, no dict
        except Exception as e:
            respuesta_texto = f"Lo siento, ocurrió un error al llamar a la API:\n`{e}`"

        # Mostrar respuesta del asistente
        with st.chat_message("assistant"):
            st.markdown(respuesta_texto)

        # Guardar en historial
        st.session_state.chat_history.append({"role": "assistant", "content": respuesta_texto})

# ****************** Nueva conversación ******************

if st.button("🗑️ Nueva conversación"):
    st.session_state.chat_history = []  # Limpiar historial de mensajes
    st.rerun()  # Recargar pagina
