import os
import streamlit as st
import time
import base64
import json
import requests
import tempfile
import logging
import traceback
import io
import sys
import toml
import re
from datetime import datetime
from pathlib import Path
from io import BytesIO
from PIL import Image
from openai import OpenAI
import uuid
import streamlit.components.v1 as components

# Importar configuración predefinida
try:
    # Intentar importar la configuración local primero (no incluida en el repositorio)
    import assistants_config_local as assistants_config
    print("Usando configuración local de asistentes")
except ImportError:
    # Si no existe, usar la configuración predeterminada
    import assistants_config
    print("Usando configuración predeterminada de asistentes")

# Importar módulo de selección de expertos
import expert_selection

# ==============================================
# APPLICATION IDENTITY DICTIONARY
# ==============================================
# Todos los elementos específicos de identidad del proyecto están centralizados aquí
# Modifique este diccionario para cambiar la identidad de la aplicación

APP_IDENTITY = {
    # Identidad principal
    "name": "Expert Nexus",
    "version": "1.0.0",
    "icon": "🔄",
    "tagline": "Múltiples Expertos, Una Sola Conversación",
    "full_title": "¡Bienvenido a Expert Nexus! 🧠🔄",
    # Información del desarrollador
    "developer": "Alexander Oviedo Fadul",
    "github_url": "https://github.com/bladealex9848",
    "website_url": "https://alexanderoviedofadul.dev/",
    "docs_url": "https://github.com/bladealex9848/expert_nexus/blob/main/README.md",
    "linkedin_url": "https://www.linkedin.com/in/alexander-oviedo-fadul/",
    "instagram_url": "https://www.instagram.com/alexander.oviedo.fadul",
    "twitter_url": "https://twitter.com/alexanderofadul",
    "facebook_url": "https://www.facebook.com/alexanderof/",
    "whatsapp_url": "https://api.whatsapp.com/send?phone=573015930519&text=Hola%20!Quiero%20conversar%20contigo!%20)",
    "repository_url": "https://github.com/bladealex9848/expert_nexus",
    # Descripción de la aplicación - formas corta y larga
    "short_description": "Tu sistema de asistentes virtuales especializados que permite cambiar entre diferentes expertos manteniendo el contexto de la conversación.",
    "long_description": """
    ### 🧠🔄 ¡Hola! Soy Expert Nexus, tu sistema avanzado de asistentes especializados

    Estoy diseñado para permitirte acceder a múltiples dominios de conocimiento a través de una interfaz unificada, manteniendo siempre el contexto completo de tu conversación.

    #### ¿Qué puedo hacer por ti hoy? 🤔

    * Proporcionarte respuestas especializadas de diferentes expertos
    * Cambiar automáticamente al experto más adecuado según tu consulta
    * Mantener el hilo completo de la conversación al cambiar de experto
    * Analizar el contenido de tus mensajes para sugerir el especialista óptimo
    * Permitirte seleccionar manualmente el experto que deseas consultar
    * Mostrarte un historial de los cambios de experto durante la conversación
    * Reiniciar la conversación cuando lo necesites sin perder el contexto

    **¡No dudes en explorar el conocimiento especializado de nuestros múltiples expertos!**

    *Recuerda: Proporciono información general basada en diferentes dominios de conocimiento. Para asesoría específica y profesional, consulta siempre a un especialista en la materia.*
    """,
    # User instructions
    "usage_instructions": """
    1. **Consulta inicial**: Escribe tu pregunta en el chat. El sistema usará el experto actual para responder.

    2. **Cambio de experto**: Si deseas cambiar de experto, utiliza el selector en la barra lateral y haz clic en "Cambiar a este experto".

    3. **Persistencia del chat**: Al cambiar de experto, el chat siempre se mantiene para preservar el contexto completo de la conversación.

    4. **Archivos adjuntos**: Puedes elegir si deseas mantener o no los archivos adjuntos al cambiar de experto.

    5. **Historial de cambios**: Puedes ver un registro cronológico de los expertos utilizados durante la conversación en la barra lateral.

    6. **Nueva conversación**: Para comenzar desde cero, haz clic en "Nueva Conversación" en la barra lateral.

    7. **Documentos adjuntos**: Puedes subir documentos para que los expertos los analicen durante la conversación.
    """,
    # Document processing information
    "document_processing_info": """
    Esta aplicación utiliza tecnología de procesamiento de texto para:

    - Analizar documentos según la especialidad del experto actual
    - Extraer información relevante para proporcionar respuestas precisas
    - Permitir que varios expertos accedan al mismo documento con diferentes perspectivas
    - Mantener los documentos disponibles al cambiar entre expertos

    **Nota sobre privacidad**: Los documentos se procesan localmente y no se almacenan permanentemente.

    **Formatos soportados**: PDF (.pdf), Texto (.txt), Markdown (.md), Imágenes (.jpg, .jpeg, .png). Otros formatos no serán procesados.
    """,
    # Texto de la interfaz de usuario
    "chat_placeholder": "¿En qué puedo ayudarte hoy? Puedes cambiar manualmente de experto en la barra lateral.",
    "file_upload_default_message": "He cargado el documento '{files}' para análisis. El experto actual lo procesará para proporcionar respuestas más precisas.",
    "badges": """
    ![Visitantes](https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fexpertnexus.streamlit.app&label=Visitantes&labelColor=%235d5d5d&countColor=%231e7ebf&style=flat)
    """,
    # Welcome message (displayed on first load)
    "welcome_message": """
    ### 🧠🔄 ¡Bienvenido a Expert Nexus!

    Soy tu sistema avanzado de asistentes especializados que permite acceder a múltiples dominios de conocimiento a través de una interfaz unificada.

    * Mantengo el contexto completo de la conversación entre cambios de experto
    * Te permito seleccionar manualmente el especialista que deseas consultar
    * Muestro qué experto está respondiendo en cada momento
    * Proporciono respuestas especializadas en áreas como transformación digital, IA, derecho, salud y más
    * Analizo documentos desde múltiples perspectivas especializadas

    **¿En qué área puedo ayudarte hoy?**
    """,
    # Mensajes de error y configuración
    "api_key_missing": "Por favor, proporciona una clave API para continuar.",
    "assistant_id_missing": "Por favor, proporciona los IDs de asistentes en el archivo secrets.toml.",
    "thread_created": "ID del hilo: ",
    "response_error": "No se pudo obtener respuesta. Por favor, intente de nuevo.",
    "config_success": "✅ Configuración completa",
    "config_warning": "⚠️ Falta configurar: {missing_items}",
    # Configuración del menú
    "menu_items": {
        "Get Help": "https://github.com/bladealex9848/expert_nexus",
        "Report a bug": None,
        "About": "Expert Nexus: Sistema avanzado de asistentes especializados que permite cambiar entre diferentes expertos durante una misma conversación, manteniendo siempre el contexto completo.",
    },
    # Footer text
    "footer_text": """
    {developer}

    [GitHub]({github_url}) | [Website]({website_url}) | [LinkedIn]({linkedin_url}) | [Instagram]({instagram_url}) | [Twitter]({twitter_url}) | [Facebook]({facebook_url}) | [WhatsApp]({whatsapp_url})
    """,
    # Log configuration
    "log_name": "expert_nexus",
    # Document naming (for exports and files)
    "document_prefix": "expert_nexus",
    "conversation_export_name": "expert_nexus_conversacion",
    # Mensajes sobre formatos de archivo
    "allowed_formats_message": "Formatos permitidos: PDF (.pdf), Texto (.txt), Markdown (.md), Imágenes (.jpg, .jpeg, .png)",
}

# Configuración avanzada de logging - Implementación multi-destino
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(
    log_dir, f"{APP_IDENTITY['log_name']}_{datetime.now().strftime('%Y%m%d')}.log"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - "
    + APP_IDENTITY["log_name"]
    + " - %(levelname)s [%(filename)s:%(lineno)d] - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(log_file)],
)

# Versión de la aplicación
APP_VERSION = APP_IDENTITY["version"]

# Configurar variables de entorno
# Sistema unificado para cargar configuración desde secrets o archivo local
logging.info("Inicializando configuración unificada para todos los entornos")

# Sistema unificado para cargar configuración desde secrets o valores predeterminados
# Detectar entorno (local o cloud) - Método mejorado
is_cloud = False

# Método 1: Verificar variable de entorno STREAMLIT_SHARING_MODE
if os.environ.get('STREAMLIT_SHARING_MODE') == 'streamlit_cloud':
    is_cloud = True
    logging.info("Entorno Cloud detectado por STREAMLIT_SHARING_MODE")

# Método 2: Verificar si estamos en un directorio típico de Streamlit Cloud
if os.path.exists('/mount/src'):
    is_cloud = True
    logging.info("Entorno Cloud detectado por directorio /mount/src")

# Método 3: Verificar hostname
try:
    import socket
    hostname = socket.gethostname()
    if 'streamlit' in hostname.lower():
        is_cloud = True
        logging.info(f"Entorno Cloud detectado por hostname: {hostname}")
except:
    pass

logging.info(f"Entorno final detectado: {'Streamlit Cloud' if is_cloud else 'Local'}")

# Inicializar con valores predeterminados (solo como fallback)
default_openai_key = assistants_config.OPENAI_API_KEY
default_mistral_key = assistants_config.MISTRAL_API_KEY
default_assistant_id = assistants_config.ASSISTANT_ID

# FORZAR DEPURACIÓN PARA STREAMLIT CLOUD
print("====================== INICIO DEPURACIÓN STREAMLIT CLOUD =======================")
print(f"Entorno detectado: {'Streamlit Cloud' if is_cloud else 'Local'}")
print(f"Directorio actual: {os.getcwd()}")
print(f"Directorio /mount/src existe: {os.path.exists('/mount/src')}")

# Verificar si st.secrets está disponible
if hasattr(st, 'secrets'):
    print("st.secrets está disponible")
    # Verificar estructura de secrets sin mostrar valores completos
    secret_keys = list(st.secrets.keys())
    print(f"Claves en st.secrets: {secret_keys}")

    # Verificar estructura plana
    if 'OPENAI_API_KEY' in st.secrets:
        key_value = st.secrets['OPENAI_API_KEY']
        key_prefix = key_value[:7] if len(key_value) > 10 else "[muy corta]"
        key_len = len(key_value)
        print(f"OPENAI_API_KEY (estructura plana): prefijo={key_prefix}..., longitud={key_len}")
    else:
        print("No se encontró OPENAI_API_KEY en estructura plana")

    # Verificar estructura anidada
    if 'openai' in st.secrets:
        openai_keys = list(st.secrets['openai'].keys())
        print(f"Claves en st.secrets['openai']: {openai_keys}")
        if 'api_key' in openai_keys:
            key_value = st.secrets['openai']['api_key']
            key_prefix = key_value[:7] if len(key_value) > 10 else "[muy corta]"
            key_len = len(key_value)
            print(f"api_key en openai: prefijo={key_prefix}..., longitud={key_len}")
        else:
            print("No se encontró api_key en st.secrets['openai']")
else:
    print("st.secrets NO está disponible")

print("====================== FIN DEPURACIÓN STREAMLIT CLOUD =======================")

# SOLUCIÓN DIRECTA PARA STREAMLIT CLOUD
# Forzar la carga de secretos independientemente del entorno
if hasattr(st, 'secrets'):
    try:
        # FORZAR CARGA DE SECRETOS PARA STREAMLIT CLOUD
        # Prioridad 1: Estructura plana (preferida)
        if 'OPENAI_API_KEY' in st.secrets:
            openai_key = st.secrets["OPENAI_API_KEY"]
            # Verificar si la clave es válida (comienza con sk- pero no es el placeholder)
            if openai_key and openai_key.startswith('sk-') and not openai_key.startswith('sk-your-'):
                # FORZAR la clave directamente en el entorno
                os.environ["OPENAI_API_KEY"] = openai_key
                print(f"FORZADO: Clave API de OpenAI cargada desde estructura plana, comienza con: {openai_key[:7]}...")
                logging.info(f"FORZADO: Clave API de OpenAI cargada desde estructura plana, comienza con: {openai_key[:7]}...")

        # Prioridad 2: Estructura anidada
        elif 'openai' in st.secrets and 'api_key' in st.secrets['openai']:
            openai_key = st.secrets["openai"]["api_key"]
            # Verificar si la clave es válida (comienza con sk- pero no es el placeholder)
            if openai_key and openai_key.startswith('sk-') and not openai_key.startswith('sk-your-'):
                # FORZAR la clave directamente en el entorno
                os.environ["OPENAI_API_KEY"] = openai_key
                print(f"FORZADO: Clave API de OpenAI cargada desde estructura anidada, comienza con: {openai_key[:7]}...")
                logging.info(f"FORZADO: Clave API de OpenAI cargada desde estructura anidada, comienza con: {openai_key[:7]}...")

        # Si no se encontró ninguna clave válida, usar el valor predeterminado
        if not os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY").startswith('sk-your-'):
            print("ADVERTENCIA: No se encontró una clave API de OpenAI válida en secrets")
            logging.warning("No se encontró una clave API de OpenAI válida en secrets")
            os.environ["OPENAI_API_KEY"] = default_openai_key

        # FORZAR CARGA DE MISTRAL API KEY
        # Prioridad 1: Estructura plana (preferida)
        if 'MISTRAL_API_KEY' in st.secrets:
            mistral_key = st.secrets["MISTRAL_API_KEY"]
            if mistral_key and not mistral_key.startswith('your-'):
                os.environ["MISTRAL_API_KEY"] = mistral_key
                print(f"FORZADO: Clave API de Mistral cargada desde estructura plana")
                logging.info("FORZADO: Clave API de Mistral cargada desde estructura plana")
        # Prioridad 2: Estructura anidada
        elif 'mistral' in st.secrets and 'api_key' in st.secrets['mistral']:
            mistral_key = st.secrets["mistral"]["api_key"]
            if mistral_key and not mistral_key.startswith('your-'):
                os.environ["MISTRAL_API_KEY"] = mistral_key
                print(f"FORZADO: Clave API de Mistral cargada desde estructura anidada")
                logging.info("FORZADO: Clave API de Mistral cargada desde estructura anidada")
        else:
            print("ADVERTENCIA: No se encontró una clave API de Mistral válida en secrets")
            logging.warning("No se encontró una clave API de Mistral válida en secrets")
            os.environ["MISTRAL_API_KEY"] = default_mistral_key

        # FORZAR CARGA DE ASSISTANT ID
        # Prioridad 1: Estructura plana (preferida)
        if 'ASSISTANT_ID' in st.secrets:
            assistant_id = st.secrets["ASSISTANT_ID"]
            if assistant_id:
                os.environ["ASSISTANT_ID"] = assistant_id
                print(f"FORZADO: ID del asistente cargado desde estructura plana: {assistant_id}")
                logging.info(f"FORZADO: ID del asistente cargado desde estructura plana: {assistant_id}")
        # Prioridad 2: Estructura anidada
        elif 'openai' in st.secrets and 'assistant_id' in st.secrets['openai']:
            assistant_id = st.secrets["openai"]["assistant_id"]
            if assistant_id:
                os.environ["ASSISTANT_ID"] = assistant_id
                print(f"FORZADO: ID del asistente cargado desde estructura anidada: {assistant_id}")
                logging.info(f"FORZADO: ID del asistente cargado desde estructura anidada: {assistant_id}")
        else:
            print(f"ADVERTENCIA: No se encontró un ID de asistente válido en secrets, usando predeterminado: {default_assistant_id}")
            logging.warning(f"No se encontró un ID de asistente válido en secrets, usando predeterminado: {default_assistant_id}")
            os.environ["ASSISTANT_ID"] = default_assistant_id

        # FORZAR CARGA DE MODELO API
        # Prioridad 1: Estructura plana (preferida)
        if 'OPENAI_API_MODEL' in st.secrets:
            modelo = st.secrets["OPENAI_API_MODEL"]
            os.environ["OPENAI_API_MODEL"] = modelo
            print(f"FORZADO: Modelo API cargado desde estructura plana: {modelo}")
            logging.info(f"FORZADO: Modelo API cargado desde estructura plana: {modelo}")
        # Prioridad 2: Estructura anidada
        elif 'openai' in st.secrets and 'api_model' in st.secrets['openai']:
            modelo = st.secrets["openai"]["api_model"]
            os.environ["OPENAI_API_MODEL"] = modelo
            print(f"FORZADO: Modelo API cargado desde estructura anidada: {modelo}")
            logging.info(f"FORZADO: Modelo API cargado desde estructura anidada: {modelo}")
        else:
            print("ADVERTENCIA: No se encontró un modelo API válido en secrets")
            logging.warning("No se encontró un modelo API válido en secrets")

    except Exception as e:
        logging.error(f"Error al cargar secrets: {str(e)}")
        # Usar valores predeterminados como fallback
        os.environ["OPENAI_API_KEY"] = default_openai_key
        os.environ["MISTRAL_API_KEY"] = default_mistral_key
        os.environ["ASSISTANT_ID"] = default_assistant_id
        logging.warning("Usando valores predeterminados debido a error al cargar secrets")

# VERIFICACIÓN FINAL DE CLAVES
# Verificar que las claves no sean placeholders
print(f"VERIFICACIÓN FINAL - OPENAI_API_KEY: {os.environ['OPENAI_API_KEY'][:7]}...")
logging.info(f"VERIFICACIÓN FINAL - OPENAI_API_KEY: {os.environ['OPENAI_API_KEY'][:7]}...")

# Intentar una última verificación y corrección
if os.environ["OPENAI_API_KEY"].startswith('sk-your-'):
    print("ALERTA: La clave API de OpenAI sigue siendo un placeholder después de todos los intentos")
    logging.error("ALERTA: La clave API de OpenAI sigue siendo un placeholder después de todos los intentos")

    # Último intento desesperado para Streamlit Cloud
    if hasattr(st, 'secrets'):
        # Verificar todas las claves disponibles
        all_keys = []
        for key in st.secrets.keys():
            all_keys.append(key)
            # Si es un diccionario, verificar sus claves también
            if isinstance(st.secrets[key], dict):
                for subkey in st.secrets[key].keys():
                    all_keys.append(f"{key}.{subkey}")

        print(f"TODAS LAS CLAVES DISPONIBLES EN SECRETS: {all_keys}")
        logging.error(f"TODAS LAS CLAVES DISPONIBLES EN SECRETS: {all_keys}")

        # Buscar cualquier clave que pueda ser una clave API de OpenAI
        for key in all_keys:
            if '.' in key:  # Clave anidada
                parent, child = key.split('.')
                if child.lower() in ['api_key', 'apikey', 'key', 'openai_api_key'] and isinstance(st.secrets[parent], dict):
                    value = st.secrets[parent][child]
                    if isinstance(value, str) and value.startswith('sk-') and not value.startswith('sk-your-'):
                        os.environ["OPENAI_API_KEY"] = value
                        print(f"RESCATE: Encontrada posible clave API en {key}: {value[:7]}...")
                        logging.info(f"RESCATE: Encontrada posible clave API en {key}: {value[:7]}...")
                        break
            else:  # Clave plana
                if key.lower() in ['api_key', 'apikey', 'key', 'openai_api_key']:
                    value = st.secrets[key]
                    if isinstance(value, str) and value.startswith('sk-') and not value.startswith('sk-your-'):
                        os.environ["OPENAI_API_KEY"] = value
                        print(f"RESCATE: Encontrada posible clave API en {key}: {value[:7]}...")
                        logging.info(f"RESCATE: Encontrada posible clave API en {key}: {value[:7]}...")
                        break

    # Mensaje de error diferente según el entorno
    if is_cloud:
        st.error("Error de configuración: La clave API de OpenAI no está configurada correctamente en Streamlit Cloud. Por favor, verifica los secretos en el panel de control de Streamlit.")
        # Mostrar instrucciones detalladas
        st.info("""
        Para configurar los secretos en Streamlit Cloud:
        1. Ve a https://share.streamlit.io/
        2. Selecciona tu aplicación 'expert_nexus'
        3. Haz clic en 'Settings' (⚙️)
        4. En la sección 'Secrets', configura los siguientes secretos:
           - OPENAI_API_KEY = "sk-tu-clave-real-de-openai"
           - ASSISTANT_ID = "tu-id-de-asistente"
           - OPENAI_API_MODEL = "gpt-4.1-nano"
           - MISTRAL_API_KEY = "tu-clave-real-de-mistral"
        5. Haz clic en 'Save'
        6. Reinicia la aplicación
        """)
    else:
        st.error("Error de configuración: La clave API de OpenAI no es válida. Por favor, configura una clave válida en secrets.toml o en assistants_config.py.")

# Configuración de página Streamlit
st.set_page_config(
    page_title=APP_IDENTITY["full_title"],
    page_icon=APP_IDENTITY["icon"],
    layout="wide",
    initial_sidebar_state="collapsed",  # Menú lateral contraído por defecto
    menu_items=APP_IDENTITY["menu_items"],
)

# Estilos CSS personalizados
st.markdown("""
<style>
    /* Estilos para la tarjeta de experto - Modo claro y oscuro */
    .expert-card {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        border-left: 4px solid #1E88E5;
    }
    /* Modo claro */
    .light .expert-card {
        background-color: #f0f2f6;
    }
    /* Modo oscuro */
    .dark .expert-card {
        background-color: #2c3e50;
    }

    /* Estilos para el historial de expertos */
    .expert-history {
        border-left: 2px solid #1E88E5;
        padding-left: 10px;
        margin-bottom: 8px;
    }

    /* Estilos para los mensajes de chat - Modo claro y oscuro */
    .expert-message {
        padding: 5px 0;
        border-radius: 4px;
    }
    /* Modo claro */
    .light .expert-message {
        background-color: #f0f7ff;
        color: #333;
    }
    /* Modo oscuro */
    .dark .expert-message {
        background-color: #1e3a5f;
        color: #f0f0f0;
    }

    /* Estilos para los botones de selección de experto */
    .stButton button {
        width: 100%;
        border-radius: 20px;
    }

    /* Estilos para el nombre del experto en los mensajes - Modo claro y oscuro */
    .expert-name {
        font-weight: bold;
        margin-bottom: 5px;
    }
    /* Modo claro */
    .light .expert-name {
        color: #1E88E5;
    }
    /* Modo oscuro */
    .dark .expert-name {
        color: #64b5f6;
    }

    /* Estilos para títulos en modo oscuro */
    .dark h1, .dark h2, .dark h3 {
        color: #f0f0f0 !important;
    }

    /* Estilos para el área de chat en modo oscuro */
    .dark .stChatMessage {
        background-color: #1e2a38 !important;
        color: #f0f0f0 !important;
    }

    /* Detector de tema */
    @media (prefers-color-scheme: dark) {
        body {
            color-scheme: dark;
        }
        body:not(.light) {
            background-color: #0e1117;
            color: #f0f0f0;
        }
    }
</style>

<script>
    // Script para detectar el tema y aplicar la clase correspondiente
    document.addEventListener('DOMContentLoaded', function() {
        const body = document.body;
        const isDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

        if (isDarkMode) {
            body.classList.add('dark');
        } else {
            body.classList.add('light');
        }

        // Escuchar cambios en el tema del sistema
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
            if (event.matches) {
                body.classList.remove('light');
                body.classList.add('dark');
            } else {
                body.classList.remove('dark');
                body.classList.add('light');
            }
        });
    });
</script>
""", unsafe_allow_html=True)


# Decorador para manejo de errores con retries
def handle_error(max_retries=2):
    """
    Decorador avanzado para manejo de errores con capacidad de reintento

    Parámetros:
        max_retries: Número máximo de reintentos ante fallos
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            last_exception = None

            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_msg = f"Error en {func.__name__} (intento {retries+1}/{max_retries+1}): {str(e)}"
                    logging.error(error_msg)

                    if retries < max_retries:
                        logging.info(f"Reintentando {func.__name__}...")
                        retries += 1
                        time.sleep(1)  # Espera antes de reintentar
                    else:
                        logging.error(
                            f"Error final después de {max_retries+1} intentos: {traceback.format_exc()}"
                        )
                        st.error(error_msg)
                        break

            return None

        return wrapper

    return decorator


# Sistema multicapa para reinicio de la aplicación
def rerun_app():
    """
    Sistema multicapa para reiniciar la aplicación Streamlit.
    Implementa múltiples estrategias de recuperación en caso de fallo.
    """
    try:
        # Método 1 (preferido): Función actual en Streamlit
        st.rerun()
    except (AttributeError, Exception) as e:
        logging.warning(f"Método primario de reinicio falló: {str(e)}")

        # Método 2: Mensaje al usuario con opción manual
        st.info("Por favor, recarga la página para ver los cambios")

        # Método 3: Intento con JavaScript nativo
        try:
            html_code = """
            <script>
                // Reintento con un retraso para permitir renderización
                setTimeout(function() {
                    window.parent.location.reload();
                }, 2000);
            </script>
            """
            st.components.v1.html(html_code, height=0, width=0)
        except Exception as e3:
            logging.error(f"Reinicio con JavaScript falló: {str(e3)}")





# Crear cliente OpenAI para Assistants
@handle_error(max_retries=1)
def create_openai_client(api_key):
    """
    Crea un cliente OpenAI con encabezados compatibles con Assistants API v2
    y verificación de conectividad
    """
    try:
        # Verificar que la clave API no sea un placeholder
        if not api_key or api_key.startswith('sk-your-'):
            error_msg = f"Clave API inválida: {api_key[:10] if len(api_key) > 10 else api_key}..."
            logging.error(error_msg)

            # Mensaje de error diferente según el entorno
            if is_cloud:
                st.error("No se pudo conectar a OpenAI: La clave API no está configurada correctamente en Streamlit Cloud. Por favor, verifica los secretos en el panel de control de Streamlit.")
            else:
                st.error(f"No se pudo conectar a OpenAI: Clave API inválida. Por favor, configura una clave válida en secrets.toml.")
            return None

        # Mostrar información de depuración (sin exponer la clave completa)
        logging.info(f"Intentando crear cliente OpenAI con clave: {api_key[:7]}...{api_key[-4:]}")

        client = OpenAI(
            api_key=api_key, default_headers={"OpenAI-Beta": "assistants=v2"}
        )

        # Verificar conectividad con una llamada simple
        try:
            models = client.models.list()
            if not models:
                raise Exception("No se pudo obtener la lista de modelos")

            # Mostrar los modelos disponibles para depuración
            model_ids = [model.id for model in models.data[:5]]
            logging.info(f"Modelos disponibles (primeros 5): {model_ids}")

            logging.info("Cliente OpenAI inicializado correctamente")
            return client
        except Exception as api_error:
            error_details = str(api_error)
            logging.error(f"Error en la llamada a la API de OpenAI: {error_details}")

            # Extraer código de error para mejor diagnóstico
            error_code = "desconocido"
            if hasattr(api_error, 'status_code'):
                error_code = api_error.status_code

            st.error(f"No se pudo conectar a OpenAI: Error code: {error_code} - {error_details}")
            return None
    except Exception as e:
        logging.error(f"Error inicializando cliente OpenAI: {str(e)}")
        st.error(f"No se pudo conectar a OpenAI: {str(e)}")
        return None


# Sistema multicapa para exportación de conversaciones
def _export_chat_to_pdf_streamlit_cloud(messages):
    """
    Método optimizado para Streamlit Cloud usando pdfkit.
    Esta implementación es compatible con el entorno de Streamlit Cloud
    y no requiere dependencias del sistema.
    """
    try:
        import pdfkit
        import markdown2
        import tempfile
        from pygments import highlight
        from pygments.lexers import get_lexer_by_name, guess_lexer
        from pygments.formatters import HtmlFormatter
        import re

        # Generar el contenido Markdown
        md_content = export_chat_to_markdown(messages)

        # Preprocesar el contenido Markdown para manejar casos especiales

        # 1. Preservar diagramas ASCII
        ascii_diagrams = []

        def preserve_ascii_diagram(match):
            diagram = match.group(1)
            ascii_diagrams.append(diagram)
            return f"\n\n```ascii-diagram-{len(ascii_diagrams)-1}\n{diagram}\n```\n\n"

        # Detectar diagramas ASCII (bloques con caracteres como │, ┌, └, ┐, ┘, ─, etc.)
        ascii_pattern = r"```(?:ascii|diagram)?\n((?:[^\n]*?[│┌└┐┘─┬┴┼┤├]+[^\n]*\n)+)```"
        md_content = re.sub(ascii_pattern, preserve_ascii_diagram, md_content)

        # 2. Manejar bloques de código con resaltado de sintaxis personalizado
        code_blocks = []

        def process_code_block(match):
            language = match.group(1) or ""
            code = match.group(2)

            # Guardar el bloque de código para procesamiento posterior
            code_blocks.append((language.strip(), code))
            return f"\n\n{{code-block-{len(code_blocks)-1}}}\n\n"

        # Extraer bloques de código
        md_content = re.sub(r"```([a-zA-Z0-9_+-]*)\n(.*?)```", process_code_block, md_content, flags=re.DOTALL)

        # 3. Convertir Markdown a HTML con markdown2 (más compatible con Streamlit Cloud)
        html_content = markdown2.markdown(
            md_content,
            extras=[
                "tables",
                "fenced-code-blocks",
                "code-friendly",
                "toc",
                "break-on-newline",
                "smarty-pants",
                "cuddled-lists",
                "footnotes"
            ]
        )

        # 4. Reemplazar los marcadores de código con HTML resaltado
        for i, (language, code) in enumerate(code_blocks):
            try:
                # Manejar diagramas ASCII preservados
                if language.startswith("ascii-diagram-"):
                    idx = int(language.split("-")[-1])
                    html_code = f'<pre class="ascii-diagram"><code>{ascii_diagrams[idx]}</code></pre>'
                else:
                    # Resaltar código con Pygments
                    if language and language != "text":
                        try:
                            lexer = get_lexer_by_name(language)
                        except:
                            lexer = guess_lexer(code)
                    else:
                        lexer = guess_lexer(code)

                    formatter = HtmlFormatter(style='default', cssclass='codehilite')
                    html_code = highlight(code, lexer, formatter)
            except Exception as e:
                # Si falla el resaltado, usar un bloque de código simple
                html_code = f'<pre><code>{code}</code></pre>'

            html_content = html_content.replace(f"{{code-block-{i}}}", html_code)

        # 5. Añadir estilos CSS avanzados para mejorar la apariencia
        css_styles = """
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            font-size: 11pt;
            color: #333;
            max-width: 100%;
            margin: 2cm;
            overflow-wrap: break-word;
        }

        h1, h2, h3, h4, h5, h6 {
            font-weight: 600;
            margin-top: 24px;
            margin-bottom: 16px;
            line-height: 1.25;
        }

        h1 {
            font-size: 2em;
            padding-bottom: 0.3em;
            border-bottom: 1px solid #eaecef;
            color: #24292e;
        }

        h2 {
            font-size: 1.5em;
            padding-bottom: 0.3em;
            border-bottom: 1px solid #eaecef;
            color: #24292e;
        }

        h3 {
            font-size: 1.25em;
            color: #24292e;
        }

        h4 {
            font-size: 1em;
            color: #24292e;
        }

        p, ul, ol, dl, table, pre {
            margin-top: 0;
            margin-bottom: 16px;
        }

        ul, ol {
            padding-left: 2em;
        }

        li + li {
            margin-top: 0.25em;
        }

        a {
            color: #0366d6;
            text-decoration: none;
        }

        table {
            border-spacing: 0;
            border-collapse: collapse;
            width: 100%;
            overflow: auto;
            margin-bottom: 16px;
        }

        table th {
            font-weight: 600;
            padding: 6px 13px;
            border: 1px solid #dfe2e5;
            background-color: #f6f8fa;
        }

        table td {
            padding: 6px 13px;
            border: 1px solid #dfe2e5;
        }

        table tr:nth-child(2n) {
            background-color: #f6f8fa;
        }

        img {
            max-width: 100%;
            height: auto;
            box-sizing: content-box;
            background-color: #fff;
        }

        code {
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            padding: 0.2em 0.4em;
            margin: 0;
            font-size: 85%;
            background-color: rgba(27, 31, 35, 0.05);
            border-radius: 3px;
        }

        pre {
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            word-wrap: normal;
            padding: 16px;
            overflow: auto;
            font-size: 85%;
            line-height: 1.45;
            background-color: #f6f8fa;
            border-radius: 3px;
            margin-bottom: 16px;
        }

        pre code {
            background-color: transparent;
            padding: 0;
            margin: 0;
            font-size: inherit;
            word-break: normal;
            white-space: pre;
            overflow: visible;
        }

        .codehilite {
            background-color: #f6f8fa;
            border-radius: 3px;
            padding: 16px;
            overflow: auto;
        }

        .codehilite .hll { background-color: #ffffcc }
        .codehilite .c { color: #999988; font-style: italic } /* Comment */
        .codehilite .err { color: #a61717; background-color: #e3d2d2 } /* Error */
        .codehilite .k { color: #000000; font-weight: bold } /* Keyword */
        .codehilite .o { color: #000000; font-weight: bold } /* Operator */
        .codehilite .cm { color: #999988; font-style: italic } /* Comment.Multiline */
        .codehilite .cp { color: #999999; font-weight: bold; font-style: italic } /* Comment.Preproc */
        .codehilite .c1 { color: #999988; font-style: italic } /* Comment.Single */
        .codehilite .cs { color: #999999; font-weight: bold; font-style: italic } /* Comment.Special */
        .codehilite .gd { color: #000000; background-color: #ffdddd } /* Generic.Deleted */
        .codehilite .ge { color: #000000; font-style: italic } /* Generic.Emph */
        .codehilite .gr { color: #aa0000 } /* Generic.Error */
        .codehilite .gh { color: #999999 } /* Generic.Heading */
        .codehilite .gi { color: #000000; background-color: #ddffdd } /* Generic.Inserted */
        .codehilite .go { color: #888888 } /* Generic.Output */
        .codehilite .gp { color: #555555 } /* Generic.Prompt */
        .codehilite .gs { font-weight: bold } /* Generic.Strong */
        .codehilite .gu { color: #aaaaaa } /* Generic.Subheading */
        .codehilite .gt { color: #aa0000 } /* Generic.Traceback */
        .codehilite .kc { color: #000000; font-weight: bold } /* Keyword.Constant */
        .codehilite .kd { color: #000000; font-weight: bold } /* Keyword.Declaration */
        .codehilite .kn { color: #000000; font-weight: bold } /* Keyword.Namespace */
        .codehilite .kp { color: #000000; font-weight: bold } /* Keyword.Pseudo */
        .codehilite .kr { color: #000000; font-weight: bold } /* Keyword.Reserved */
        .codehilite .kt { color: #445588; font-weight: bold } /* Keyword.Type */
        .codehilite .m { color: #009999 } /* Literal.Number */
        .codehilite .s { color: #d01040 } /* Literal.String */
        .codehilite .na { color: #008080 } /* Name.Attribute */
        .codehilite .nb { color: #0086B3 } /* Name.Builtin */
        .codehilite .nc { color: #445588; font-weight: bold } /* Name.Class */
        .codehilite .no { color: #008080 } /* Name.Constant */
        .codehilite .nd { color: #3c5d5d; font-weight: bold } /* Name.Decorator */
        .codehilite .ni { color: #800080 } /* Name.Entity */
        .codehilite .ne { color: #990000; font-weight: bold } /* Name.Exception */
        .codehilite .nf { color: #990000; font-weight: bold } /* Name.Function */
        .codehilite .nl { color: #990000; font-weight: bold } /* Name.Label */
        .codehilite .nn { color: #555555 } /* Name.Namespace */
        .codehilite .nt { color: #000080 } /* Name.Tag */
        .codehilite .nv { color: #008080 } /* Name.Variable */
        .codehilite .ow { color: #000000; font-weight: bold } /* Operator.Word */
        .codehilite .w { color: #bbbbbb } /* Text.Whitespace */
        .codehilite .mf { color: #009999 } /* Literal.Number.Float */
        .codehilite .mh { color: #009999 } /* Literal.Number.Hex */
        .codehilite .mi { color: #009999 } /* Literal.Number.Integer */
        .codehilite .mo { color: #009999 } /* Literal.Number.Oct */
        .codehilite .sb { color: #d01040 } /* Literal.String.Backtick */
        .codehilite .sc { color: #d01040 } /* Literal.String.Char */
        .codehilite .sd { color: #d01040 } /* Literal.String.Doc */
        .codehilite .s2 { color: #d01040 } /* Literal.String.Double */
        .codehilite .se { color: #d01040 } /* Literal.String.Escape */
        .codehilite .sh { color: #d01040 } /* Literal.String.Heredoc */
        .codehilite .si { color: #d01040 } /* Literal.String.Interpol */
        .codehilite .sx { color: #d01040 } /* Literal.String.Other */
        .codehilite .sr { color: #009926 } /* Literal.String.Regex */
        .codehilite .s1 { color: #d01040 } /* Literal.String.Single */
        .codehilite .ss { color: #990073 } /* Literal.String.Symbol */
        .codehilite .bp { color: #999999 } /* Name.Builtin.Pseudo */
        .codehilite .vc { color: #008080 } /* Name.Variable.Class */
        .codehilite .vg { color: #008080 } /* Name.Variable.Global */
        .codehilite .vi { color: #008080 } /* Name.Variable.Instance */
        .codehilite .il { color: #009999 } /* Literal.Number.Integer.Long */

        .ascii-diagram {
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            line-height: 1.2;
            white-space: pre;
            background-color: #f6f8fa;
            padding: 16px;
            border-radius: 3px;
        }

        blockquote {
            padding: 0 1em;
            color: #6a737d;
            border-left: 0.25em solid #dfe2e5;
            margin: 0 0 16px 0;
        }

        hr {
            height: 0.25em;
            padding: 0;
            margin: 24px 0;
            background-color: #e1e4e8;
            border: 0;
        }

        .footnote {
            font-size: 0.8em;
            color: #6a737d;
        }

        /* Estilos específicos para la conversación */
        .message {
            margin-bottom: 20px;
            padding: 10px;
            border-radius: 5px;
        }

        .user-message {
            background-color: #f1f8ff;
            border-left: 4px solid #0366d6;
        }

        .assistant-message {
            background-color: #f6f8fa;
            border-left: 4px solid #28a745;
        }

        .message-header {
            font-weight: bold;
            margin-bottom: 5px;
            color: #24292e;
        }

        .timestamp {
            font-size: 0.8em;
            color: #6a737d;
        }
        """

        # 6. Crear HTML completo con estilos
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{APP_IDENTITY["conversation_export_name"]}</title>
            <style>
                {css_styles}
            </style>
        </head>
        <body>
            <h1>{APP_IDENTITY["conversation_export_name"]}</h1>
            <p class="timestamp">Exportado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            <hr>
            {html_content}
        </body>
        </html>
        """

        # 7. Crear un archivo temporal para el HTML
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as html_file:
            html_file.write(full_html.encode('utf-8'))
            html_path = html_file.name

        # 8. Configurar opciones para pdfkit
        options = {
            'page-size': 'A4',
            'margin-top': '2cm',
            'margin-right': '2cm',
            'margin-bottom': '2cm',
            'margin-left': '2cm',
            'encoding': 'UTF-8',
            'no-outline': None,
            'enable-local-file-access': None
        }

        # 9. Crear un archivo temporal para el PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_file:
            pdf_path = pdf_file.name

        # 10. Convertir HTML a PDF usando pdfkit o métodos alternativos
        pdf_generated = False

        # Método 1: Intentar usar pdfkit con wkhtmltopdf del sistema
        try:
            pdfkit.from_file(html_path, pdf_path, options=options)
            pdf_generated = True
            logging.info("PDF generado con pdfkit usando wkhtmltopdf del sistema")
        except Exception as e:
            logging.warning(f"Error al usar wkhtmltopdf del sistema: {str(e)}")

            # Método 2: Intentar usar pdfkit con wkhtmltopdf en ubicaciones alternativas
            try:
                import os
                import platform

                # Diferentes ubicaciones según el sistema operativo
                wkhtmltopdf_path = None
                system = platform.system().lower()

                if system == 'darwin':  # macOS
                    possible_paths = [
                        '/usr/local/bin/wkhtmltopdf',
                        '/opt/homebrew/bin/wkhtmltopdf',
                        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'wkhtmltopdf')
                    ]
                elif system == 'linux':
                    possible_paths = [
                        '/usr/bin/wkhtmltopdf',
                        '/usr/local/bin/wkhtmltopdf',
                        '/app/.heroku/python/bin/wkhtmltopdf',  # Streamlit Cloud
                        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'wkhtmltopdf')
                    ]
                else:  # Windows
                    possible_paths = [
                        'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe',
                        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'wkhtmltopdf.exe')
                    ]

                # Probar cada ubicación
                for path in possible_paths:
                    if os.path.exists(path):
                        wkhtmltopdf_path = path
                        logging.info(f"wkhtmltopdf encontrado en: {path}")
                        break

                if wkhtmltopdf_path:
                    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
                    pdfkit.from_file(html_path, pdf_path, options=options, configuration=config)
                    pdf_generated = True
                    logging.info(f"PDF generado con pdfkit usando wkhtmltopdf en: {wkhtmltopdf_path}")
                else:
                    logging.warning("No se encontró wkhtmltopdf en ninguna ubicación conocida")
            except Exception as e2:
                logging.warning(f"Error al usar wkhtmltopdf alternativo: {str(e2)}")

            # Método 3: Usar un método alternativo si pdfkit falló
            if not pdf_generated:
                try:
                    # Intentar usar FPDF para convertir el HTML a PDF
                    from fpdf import FPDF
                    import html2text

                    # Convertir HTML a texto plano
                    h = html2text.HTML2Text()
                    h.ignore_links = False
                    text_content = h.handle(full_html)

                    # Crear PDF con FPDF
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)

                    # Dividir el texto en líneas y añadirlas al PDF
                    for line in text_content.split('\n'):
                        if line.strip():
                            pdf.multi_cell(0, 10, line)

                    # Guardar el PDF
                    pdf.output(pdf_path)
                    pdf_generated = True
                    logging.info("PDF generado con FPDF como alternativa")
                except Exception as e3:
                    logging.warning(f"Error al usar FPDF como alternativa: {str(e3)}")

                    # Si todo lo anterior falló, lanzar la excepción original
                    if not pdf_generated:
                        raise e

        # 11. Leer el contenido del PDF
        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()

        # 12. Limpiar archivos temporales
        try:
            os.unlink(html_path)
            os.unlink(pdf_path)
        except Exception as e:
            logging.warning(f"Error al eliminar archivos temporales: {str(e)}")

        return pdf_content, "pdf"

    except Exception as e:
        logging.error(f"Error en la conversión de Markdown a PDF con pdfkit: {str(e)}")
        raise e

def export_chat_to_pdf(messages):
    """
    Sistema multicapa para exportación de conversaciones a PDF.
    Implementa múltiples estrategias de generación con manejo de fallos.

    Ahora con soporte para conversión de Markdown a PDF usando MDPDFusion.
    """
    # Importar módulos necesarios
    import os
    import tempfile

    # Detectar si estamos en Streamlit Cloud
    is_streamlit_cloud = False
    if os.environ.get('STREAMLIT_SHARING_MODE') == 'streamlit_cloud':
        is_streamlit_cloud = True
        logging.info("Detectado entorno Streamlit Cloud")

    # Verificar si MDPDFusion está disponible
    mdpdfusion_available = False
    try:
        from mdpdfusion import convert_md_to_pdf
        mdpdfusion_available = True
        logging.info("MDPDFusion disponible para exportación a PDF")
    except ImportError:
        logging.info("MDPDFusion no disponible, se usarán métodos alternativos")

    # Verificar dependencias necesarias para los diferentes métodos
    pdfkit_available = False
    try:
        import pdfkit
        pdfkit_available = True
        logging.info("pdfkit disponible para exportación a PDF")
    except ImportError:
        logging.info("pdfkit no disponible")

    markdown2_available = False
    try:
        import markdown2
        markdown2_available = True
        logging.info("markdown2 disponible para exportación a PDF")
    except ImportError:
        logging.info("markdown2 no disponible")

    # Método MDPDFusion (primera opción)
    if mdpdfusion_available:
        try:
            logging.info("Usando método MDPDFusion para exportación a PDF")

            # Generar el contenido Markdown
            md_content = export_chat_to_markdown(messages)

            # Guardar el contenido Markdown en un archivo temporal
            with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as md_file:
                md_file.write(md_content.encode('utf-8'))
                md_path = md_file.name

            # Crear un directorio temporal para el PDF
            temp_dir = tempfile.mkdtemp()

            # Convertir el archivo Markdown a PDF
            output_pdf = convert_md_to_pdf(md_path, temp_dir)

            # Leer el contenido del PDF
            if output_pdf and os.path.exists(output_pdf):
                with open(output_pdf, 'rb') as pdf_file:
                    pdf_content = pdf_file.read()

                # Limpiar archivos temporales
                os.unlink(md_path)
                os.unlink(output_pdf)
                os.rmdir(temp_dir)

                logging.info("Conversión exitosa con MDPDFusion")
                return pdf_content, "pdf"
            else:
                logging.warning("MDPDFusion no generó un archivo PDF válido")
        except Exception as e:
            logging.warning(f"Método MDPDFusion falló: {str(e)}")

    # Método optimizado para Streamlit Cloud
    if is_streamlit_cloud and pdfkit_available and markdown2_available:
        try:
            logging.info("Usando método pdfkit optimizado para Streamlit Cloud")
            return _export_chat_to_pdf_streamlit_cloud(messages)
        except Exception as e:
            logging.warning(f"Método pdfkit para Streamlit Cloud falló: {str(e)}")

    # Intentar con pdfkit como método principal en entorno local
    if pdfkit_available and markdown2_available:
        try:
            logging.info("Intentando método pdfkit como método principal")
            return _export_chat_to_pdf_streamlit_cloud(messages)
        except Exception as e:
            logging.warning(f"Método pdfkit falló: {str(e)}")

    # Métodos alternativos que no dependen de bibliotecas del sistema
    try:
        # Método 1: FPDF con manejo mejorado
        logging.info("Intentando método FPDF para exportación a PDF")
        return _export_chat_to_pdf_primary(messages)
    except Exception as e1:
        logging.warning(f"Método FPDF falló: {str(e1)}")
        try:
            # Método 2: ReportLab como alternativa
            logging.info("Intentando método ReportLab para exportación a PDF")
            return _export_chat_to_pdf_secondary(messages)
        except Exception as e2:
            logging.warning(f"Método ReportLab falló: {str(e2)}")
            try:
                # Método 3: Conversión simple como último recurso
                logging.info("Intentando método de respaldo simple para exportación a PDF")
                return _export_chat_to_pdf_fallback(messages)
            except Exception as e3:
                logging.error(f"Todos los métodos de exportación a PDF fallaron: {str(e3)}")
                # Último recurso: Devolver contenido en markdown codificado
                logging.info("Fallback a exportación Markdown")
                md_content = export_chat_to_markdown(messages)
                st.warning("No fue posible generar un PDF. Se ha creado un archivo markdown en su lugar.")
                return base64.b64encode(md_content.encode()).decode(), "markdown"


def _export_chat_to_pdf_from_markdown(messages):
    """
    Método avanzado basado en WeasyPrint para convertir Markdown a PDF.
    Utiliza la técnica del proyecto MDPDFusion con soporte mejorado para:
    - Sintaxis Markdown completa
    - Bloques de código con resaltado de sintaxis
    - Tablas con formato visual adecuado
    - Enlaces internos funcionales
    - Imágenes con ajuste automático
    - Diagramas ASCII preservados
    """
    try:
        # Importar las bibliotecas necesarias
        import os
        import tempfile
        import re
        import base64
        import markdown

        # Intentar importar WeasyPrint y sus dependencias
        try:
            from weasyprint import HTML, CSS
            from weasyprint.text.fonts import FontConfiguration
        except ImportError:
            logging.warning("WeasyPrint no está disponible. No se puede usar el método avanzado de conversión.")
            raise

        # Intentar importar Pygments para resaltado de sintaxis
        try:
            from pygments import highlight
            from pygments.lexers import get_lexer_by_name, guess_lexer
            from pygments.formatters import HtmlFormatter
        except ImportError:
            logging.warning("Pygments no está disponible. El resaltado de sintaxis será limitado.")
            raise

        # Generar el contenido Markdown
        md_content = export_chat_to_markdown(messages)

        # Preprocesar el contenido Markdown para manejar casos especiales

        # 1. Preservar diagramas ASCII
        ascii_diagrams = []

        def preserve_ascii_diagram(match):
            diagram = match.group(1)
            ascii_diagrams.append(diagram)
            return f"\n\n```ascii-diagram-{len(ascii_diagrams)-1}\n{diagram}\n```\n\n"

        # Detectar diagramas ASCII (bloques con caracteres como │, ┌, └, ┐, ┘, ─, etc.)
        ascii_pattern = r"```(?:ascii|diagram)?\n((?:[^\n]*?[│┌└┐┘─┬┴┼┤├]+[^\n]*\n)+)```"
        md_content = re.sub(ascii_pattern, preserve_ascii_diagram, md_content)

        # 2. Manejar bloques de código con resaltado de sintaxis personalizado
        code_blocks = []

        def process_code_block(match):
            language = match.group(1) or ""
            code = match.group(2)

            # Guardar el bloque de código para procesamiento posterior
            code_blocks.append((language.strip(), code))
            return f"\n\n{{code-block-{len(code_blocks)-1}}}\n\n"

        # Extraer bloques de código
        md_content = re.sub(r"```([a-zA-Z0-9_+-]*)\n(.*?)```", process_code_block, md_content, flags=re.DOTALL)

        # 3. Convertir Markdown a HTML con extensiones avanzadas
        # Definir las extensiones básicas que siempre están disponibles
        extensions = [
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
            'markdown.extensions.nl2br'
        ]

        # Intentar añadir extensiones adicionales si están disponibles
        try:
            import importlib
            additional_extensions = [
                'markdown.extensions.sane_lists',
                'markdown.extensions.smarty',
                'markdown.extensions.attr_list',
                'markdown.extensions.def_list',
                'markdown.extensions.abbr',
                'markdown.extensions.footnotes',
                'markdown.extensions.md_in_html'
            ]

            # Verificar cada extensión antes de añadirla
            for ext in additional_extensions:
                try:
                    importlib.import_module(ext)
                    extensions.append(ext)
                except ImportError:
                    logging.warning(f"Extensión Markdown no disponible: {ext}")
        except Exception as e:
            logging.warning(f"Error al cargar extensiones adicionales de Markdown: {str(e)}")

        # Convertir Markdown a HTML con las extensiones disponibles
        html_content = markdown.markdown(
            md_content,
            extensions=extensions,
            extension_configs={
                'markdown.extensions.codehilite': {
                    'linenums': False,
                    'guess_lang': False
                }
            }
        )

        # 4. Reemplazar los marcadores de código con HTML resaltado
        for i, (language, code) in enumerate(code_blocks):
            try:
                # Manejar diagramas ASCII preservados
                if language.startswith("ascii-diagram-"):
                    idx = int(language.split("-")[-1])
                    html_code = f'<pre class="ascii-diagram"><code>{ascii_diagrams[idx]}</code></pre>'
                else:
                    # Resaltar código con Pygments
                    if language and language != "text":
                        try:
                            lexer = get_lexer_by_name(language)
                        except:
                            lexer = guess_lexer(code)
                    else:
                        lexer = guess_lexer(code)

                    formatter = HtmlFormatter(style='default', cssclass='codehilite')
                    html_code = highlight(code, lexer, formatter)
            except Exception as e:
                # Si falla el resaltado, usar un bloque de código simple
                html_code = f'<pre><code>{code}</code></pre>'

            html_content = html_content.replace(f"{{code-block-{i}}}", html_code)

        # 5. Añadir estilos CSS avanzados para mejorar la apariencia
        css_styles = """
        @page {
            margin: 2cm;
            @top-right {
                content: "Expert Nexus";
                font-size: 9pt;
                color: #888;
            }
            @bottom-center {
                content: counter(page);
                font-size: 9pt;
            }
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            font-size: 11pt;
            color: #333;
            max-width: 100%;
            overflow-wrap: break-word;
        }

        h1, h2, h3, h4, h5, h6 {
            font-weight: 600;
            margin-top: 24px;
            margin-bottom: 16px;
            line-height: 1.25;
        }

        h1 {
            font-size: 2em;
            padding-bottom: 0.3em;
            border-bottom: 1px solid #eaecef;
            color: #24292e;
        }

        h2 {
            font-size: 1.5em;
            padding-bottom: 0.3em;
            border-bottom: 1px solid #eaecef;
            color: #24292e;
        }

        h3 {
            font-size: 1.25em;
            color: #24292e;
        }

        h4 {
            font-size: 1em;
            color: #24292e;
        }

        p, ul, ol, dl, table, pre {
            margin-top: 0;
            margin-bottom: 16px;
        }

        ul, ol {
            padding-left: 2em;
        }

        li + li {
            margin-top: 0.25em;
        }

        a {
            color: #0366d6;
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }

        table {
            border-spacing: 0;
            border-collapse: collapse;
            width: 100%;
            overflow: auto;
            margin-bottom: 16px;
        }

        table th {
            font-weight: 600;
            padding: 6px 13px;
            border: 1px solid #dfe2e5;
            background-color: #f6f8fa;
        }

        table td {
            padding: 6px 13px;
            border: 1px solid #dfe2e5;
        }

        table tr:nth-child(2n) {
            background-color: #f6f8fa;
        }

        img {
            max-width: 100%;
            height: auto;
            box-sizing: content-box;
            background-color: #fff;
        }

        code {
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            padding: 0.2em 0.4em;
            margin: 0;
            font-size: 85%;
            background-color: rgba(27, 31, 35, 0.05);
            border-radius: 3px;
        }

        pre {
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            word-wrap: normal;
            padding: 16px;
            overflow: auto;
            font-size: 85%;
            line-height: 1.45;
            background-color: #f6f8fa;
            border-radius: 3px;
            margin-bottom: 16px;
        }

        pre code {
            background-color: transparent;
            padding: 0;
            margin: 0;
            font-size: inherit;
            word-break: normal;
            white-space: pre;
            overflow: visible;
        }

        .codehilite {
            background-color: #f6f8fa;
            border-radius: 3px;
            padding: 16px;
            overflow: auto;
        }

        .codehilite .hll { background-color: #ffffcc }
        .codehilite .c { color: #999988; font-style: italic } /* Comment */
        .codehilite .err { color: #a61717; background-color: #e3d2d2 } /* Error */
        .codehilite .k { color: #000000; font-weight: bold } /* Keyword */
        .codehilite .o { color: #000000; font-weight: bold } /* Operator */
        .codehilite .cm { color: #999988; font-style: italic } /* Comment.Multiline */
        .codehilite .cp { color: #999999; font-weight: bold; font-style: italic } /* Comment.Preproc */
        .codehilite .c1 { color: #999988; font-style: italic } /* Comment.Single */
        .codehilite .cs { color: #999999; font-weight: bold; font-style: italic } /* Comment.Special */
        .codehilite .gd { color: #000000; background-color: #ffdddd } /* Generic.Deleted */
        .codehilite .ge { color: #000000; font-style: italic } /* Generic.Emph */
        .codehilite .gr { color: #aa0000 } /* Generic.Error */
        .codehilite .gh { color: #999999 } /* Generic.Heading */
        .codehilite .gi { color: #000000; background-color: #ddffdd } /* Generic.Inserted */
        .codehilite .go { color: #888888 } /* Generic.Output */
        .codehilite .gp { color: #555555 } /* Generic.Prompt */
        .codehilite .gs { font-weight: bold } /* Generic.Strong */
        .codehilite .gu { color: #aaaaaa } /* Generic.Subheading */
        .codehilite .gt { color: #aa0000 } /* Generic.Traceback */
        .codehilite .kc { color: #000000; font-weight: bold } /* Keyword.Constant */
        .codehilite .kd { color: #000000; font-weight: bold } /* Keyword.Declaration */
        .codehilite .kn { color: #000000; font-weight: bold } /* Keyword.Namespace */
        .codehilite .kp { color: #000000; font-weight: bold } /* Keyword.Pseudo */
        .codehilite .kr { color: #000000; font-weight: bold } /* Keyword.Reserved */
        .codehilite .kt { color: #445588; font-weight: bold } /* Keyword.Type */
        .codehilite .m { color: #009999 } /* Literal.Number */
        .codehilite .s { color: #d01040 } /* Literal.String */
        .codehilite .na { color: #008080 } /* Name.Attribute */
        .codehilite .nb { color: #0086B3 } /* Name.Builtin */
        .codehilite .nc { color: #445588; font-weight: bold } /* Name.Class */
        .codehilite .no { color: #008080 } /* Name.Constant */
        .codehilite .nd { color: #3c5d5d; font-weight: bold } /* Name.Decorator */
        .codehilite .ni { color: #800080 } /* Name.Entity */
        .codehilite .ne { color: #990000; font-weight: bold } /* Name.Exception */
        .codehilite .nf { color: #990000; font-weight: bold } /* Name.Function */
        .codehilite .nl { color: #990000; font-weight: bold } /* Name.Label */
        .codehilite .nn { color: #555555 } /* Name.Namespace */
        .codehilite .nt { color: #000080 } /* Name.Tag */
        .codehilite .nv { color: #008080 } /* Name.Variable */
        .codehilite .ow { color: #000000; font-weight: bold } /* Operator.Word */
        .codehilite .w { color: #bbbbbb } /* Text.Whitespace */
        .codehilite .mf { color: #009999 } /* Literal.Number.Float */
        .codehilite .mh { color: #009999 } /* Literal.Number.Hex */
        .codehilite .mi { color: #009999 } /* Literal.Number.Integer */
        .codehilite .mo { color: #009999 } /* Literal.Number.Oct */
        .codehilite .sb { color: #d01040 } /* Literal.String.Backtick */
        .codehilite .sc { color: #d01040 } /* Literal.String.Char */
        .codehilite .sd { color: #d01040 } /* Literal.String.Doc */
        .codehilite .s2 { color: #d01040 } /* Literal.String.Double */
        .codehilite .se { color: #d01040 } /* Literal.String.Escape */
        .codehilite .sh { color: #d01040 } /* Literal.String.Heredoc */
        .codehilite .si { color: #d01040 } /* Literal.String.Interpol */
        .codehilite .sx { color: #d01040 } /* Literal.String.Other */
        .codehilite .sr { color: #009926 } /* Literal.String.Regex */
        .codehilite .s1 { color: #d01040 } /* Literal.String.Single */
        .codehilite .ss { color: #990073 } /* Literal.String.Symbol */
        .codehilite .bp { color: #999999 } /* Name.Builtin.Pseudo */
        .codehilite .vc { color: #008080 } /* Name.Variable.Class */
        .codehilite .vg { color: #008080 } /* Name.Variable.Global */
        .codehilite .vi { color: #008080 } /* Name.Variable.Instance */
        .codehilite .il { color: #009999 } /* Literal.Number.Integer.Long */

        .ascii-diagram {
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            line-height: 1.2;
            white-space: pre;
            background-color: #f6f8fa;
            padding: 16px;
            border-radius: 3px;
        }

        blockquote {
            padding: 0 1em;
            color: #6a737d;
            border-left: 0.25em solid #dfe2e5;
            margin: 0 0 16px 0;
        }

        hr {
            height: 0.25em;
            padding: 0;
            margin: 24px 0;
            background-color: #e1e4e8;
            border: 0;
        }

        .footnote {
            font-size: 0.8em;
            color: #6a737d;
        }

        /* Estilos específicos para la conversación */
        .message {
            margin-bottom: 20px;
            padding: 10px;
            border-radius: 5px;
        }

        .user-message {
            background-color: #f1f8ff;
            border-left: 4px solid #0366d6;
        }

        .assistant-message {
            background-color: #f6f8fa;
            border-left: 4px solid #28a745;
        }

        .message-header {
            font-weight: bold;
            margin-bottom: 5px;
            color: #24292e;
        }

        .timestamp {
            font-size: 0.8em;
            color: #6a737d;
        }
        """

        # 6. Crear HTML completo con estilos
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{APP_IDENTITY["conversation_export_name"]}</title>
            <style>
                {css_styles}
            </style>
        </head>
        <body>
            <h1>{APP_IDENTITY["conversation_export_name"]}</h1>
            <p class="timestamp">Exportado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            <hr>
            {html_content}
        </body>
        </html>
        """

        # 7. Configurar fuentes
        font_config = FontConfiguration()

        # 8. Crear PDF desde HTML
        html = HTML(string=full_html)

        # 9. Crear un archivo temporal para el PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            # Generar el PDF
            html.write_pdf(
                tmp.name,
                font_config=font_config,
                presentational_hints=True
            )

            # Leer el contenido del PDF
            tmp.seek(0)
            pdf_content = tmp.read()

        return pdf_content, "pdf"

    except Exception as e:
        logging.error(f"Error en la conversión de Markdown a PDF: {str(e)}")
        raise e


def _export_chat_to_pdf_primary(messages):
    """
    Método primario: FPDF optimizado con manejo de errores mejorado
    y división inteligente de texto para evitar problemas de espacio.
    Este método está optimizado para funcionar en Streamlit Cloud.
    """
    try:
        from fpdf import FPDF
    except ImportError:
        # Intentar con fpdf2 que es más compatible con Streamlit Cloud
        from fpdf2 import FPDF
    import re

    class CustomPDF(FPDF):
        def header(self):
            self.set_font("helvetica", "B", 12)
            self.cell(
                0,
                10,
                f'{APP_IDENTITY["name"]} - Historial de Conversación',
                0,
                new_y="NEXT",
                align="C",
            )
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font("helvetica", "I", 8)
            self.cell(0, 10, f"Página {self.page_no()}", 0, 0, "C")

        def add_message(self, role, content):
            # Añadir título del mensaje
            self.set_font("helvetica", "B", 11)
            self.cell(0, 10, role, 0, new_y="NEXT", align="L")
            self.ln(2)

            # Añadir contenido con procesamiento seguro
            self.set_font("helvetica", "", 10)
            self._safe_add_content(content)
            self.ln(5)

        def _safe_add_content(self, content):
            # Procesar markdown básico
            content = self._process_markdown(content)

            # Dividir en párrafos
            paragraphs = content.split("\n\n")

            for paragraph in paragraphs:
                if not paragraph.strip():
                    self.ln(5)
                    continue

                # Dividir párrafos largos en líneas seguras
                lines = self._safe_wrap_text(paragraph, max_width=180)

                for line in lines:
                    if not line.strip():
                        continue

                    if line.startswith("- ") or line.startswith("* "):
                        # Elemento de lista
                        self.cell(5, 10, "", 0, 0)
                        self.cell(5, 10, "•", 0, 0)
                        self._safe_multi_cell(0, 10, line[2:])
                    else:
                        # Párrafo normal
                        self._safe_multi_cell(0, 10, line)

                # Espacio entre párrafos
                self.ln(2)

        def _process_markdown(self, text):
            # Simplificar encabezados
            text = re.sub(r"^#{1,6}\s+(.*?)$", r"\1", text, flags=re.MULTILINE)

            # Eliminar elementos multimedia
            text = re.sub(r"!\[.*?\]\(.*?\)", "[IMAGEN]", text)

            # Simplificar enlaces
            text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)

            return text

        def _safe_wrap_text(self, text, max_width=180):
            """Divide texto en líneas seguras para renderizar"""
            lines = []
            for raw_line in text.split("\n"):
                if len(raw_line) < max_width:
                    lines.append(raw_line)
                    continue

                # Dividir líneas largas en palabras
                words = raw_line.split(" ")
                current_line = ""

                for word in words:
                    test_line = current_line + " " + word if current_line else word

                    if len(test_line) <= max_width:
                        current_line = test_line
                    else:
                        lines.append(current_line)
                        current_line = word

                if current_line:
                    lines.append(current_line)

            return lines

        def _safe_multi_cell(self, w, h, txt, border=0, align="J", fill=False):
            """Versión segura de multi_cell con manejo de errores integrado"""
            try:
                # Eliminar caracteres no ASCII si es necesario
                if not all(ord(c) < 128 for c in txt):
                    txt = "".join(c if ord(c) < 128 else "?" for c in txt)

                # Limitar longitud de línea si es necesario
                if len(txt) > 200:
                    chunks = [txt[i : i + 200] for i in range(0, len(txt), 200)]
                    for chunk in chunks:
                        self.multi_cell(w, h, chunk, border, align, fill)
                else:
                    self.multi_cell(w, h, txt, border, align, fill)
            except Exception as e:
                logging.warning(
                    f"Error en multi_cell: {str(e)}. Intentando versión simplificada."
                )
                # Versión de respaldo extremadamente simplificada
                safe_txt = "".join(c for c in txt if c.isalnum() or c in " .,;:-?!()")
                self.multi_cell(w, h, safe_txt[:100] + "...", border, align, fill)

    # Crear el PDF
    pdf = CustomPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Añadir fecha
    pdf.set_font("helvetica", "I", 10)
    pdf.cell(
        0, 10, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, new_y="NEXT"
    )
    pdf.ln(5)

    # Añadir mensajes
    for msg in messages:
        role = "Usuario" if msg["role"] == "user" else APP_IDENTITY["name"]
        pdf.add_message(role, msg["content"])

    # Generar PDF
    output = io.BytesIO()
    pdf.output(output)
    return output.getvalue(), "pdf"


def _export_chat_to_pdf_secondary(messages):
    """
    Método secundario: ReportLab para generación alternativa de PDF
    con manejo mejorado de texto extenso.
    Este método está optimizado para funcionar en Streamlit Cloud.
    """
    try:
        # Importar con manejo de errores para mayor compatibilidad
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.platypus import PageBreak  # Importar por separado para evitar errores
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
    except ImportError as e:
        logging.error(f"Error importando ReportLab: {str(e)}")
        raise e
    from reportlab.lib import colors

    # Crear buffer y documento
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
    )

    # Configurar estilos
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="Title",
            fontName="Helvetica-Bold",
            fontSize=14,
            alignment=1,
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="User",
            fontName="Helvetica-Bold",
            fontSize=12,
            textColor=colors.blue,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Assistant",
            fontName="Helvetica-Bold",
            fontSize=12,
            textColor=colors.green,
            spaceAfter=6,
        )
    )

    # Elementos del documento
    elements = []

    # Título y fecha
    elements.append(
        Paragraph(
            f"{APP_IDENTITY['name']} - Historial de Conversación", styles["Title"]
        )
    )
    elements.append(Spacer(1, 0.25 * inch))
    elements.append(
        Paragraph(
            f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Italic"]
        )
    )
    elements.append(Spacer(1, 0.25 * inch))

    # Función de seguridad para procesar texto
    def safe_process_text(text, max_chunk=2000):
        # Escapar caracteres especiales HTML
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        # Convertir newlines a <br/>
        text = text.replace("\n", "<br/>")

        # Dividir texto muy largo en secciones manejables
        if len(text) > max_chunk:
            chunks = []
            for i in range(0, len(text), max_chunk):
                chunks.append(text[i : i + max_chunk])
            return chunks
        return [text]

    # Procesar mensajes
    for msg in messages:
        role = "Usuario" if msg["role"] == "user" else APP_IDENTITY["name"]
        style = styles["User"] if msg["role"] == "user" else styles["Assistant"]

        # Título del mensaje
        elements.append(Paragraph(role, style))

        # Contenido procesado en porciones seguras
        content_chunks = safe_process_text(msg["content"])
        for i, chunk in enumerate(content_chunks):
            try:
                elements.append(Paragraph(chunk, styles["Normal"]))
                if i < len(content_chunks) - 1:
                    elements.append(Spacer(1, 0.1 * inch))
            except Exception as e:
                logging.warning(f"Error al procesar chunk {i}: {str(e)}")
                # Versión ultra simplificada como respaldo
                elements.append(
                    Paragraph(
                        "[Contenido simplificado debido a error de formato]",
                        styles["Normal"],
                    )
                )

        elements.append(Spacer(1, 0.2 * inch))

    # Generar documento con manejo de errores
    try:
        doc.build(elements)
        pdf_data = buffer.getvalue()
        buffer.close()
        return pdf_data, "pdf"
    except Exception as e:
        logging.error(f"Error en ReportLab: {str(e)}")
        raise e


def _export_chat_to_pdf_fallback(messages):
    """
    Método de último recurso: PDF simple sin formato avanzado
    diseñado para máxima compatibilidad y robustez
    """
    from fpdf import FPDF

    # PDF básico con manejo mínimo
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)

    # Título
    pdf.set_font("helvetica", style="B", size=16)
    pdf.cell(
        200,
        10,
        f"{APP_IDENTITY['name']} - Historial de Conversación",
        ln=True,
        align="C",
    )
    pdf.ln(5)

    # Fecha
    pdf.set_font("helvetica", style="I", size=10)
    pdf.cell(200, 10, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(10)

    # Mensajes - formato mínimo con máxima seguridad
    pdf.set_font("helvetica", size=11)
    for msg in messages:
        role = "Usuario" if msg["role"] == "user" else APP_IDENTITY["name"]

        # Encabezado del mensaje
        pdf.set_font("helvetica", style="B", size=12)
        pdf.cell(200, 10, role, ln=True)
        pdf.ln(2)

        # Contenido ultra-simple, sin formato
        pdf.set_font("helvetica", size=10)

        # Extraer texto plano con máxima seguridad
        simple_text = "".join(c if ord(c) < 128 else "?" for c in msg["content"])
        simple_text = simple_text.replace("\n", " ").replace("\r", "")

        # Dividir texto en líneas muy cortas para evitar errores
        line_length = 50  # Longitud muy conservadora
        for i in range(0, len(simple_text), line_length):
            chunk = simple_text[i : i + line_length]
            try:
                pdf.cell(0, 10, chunk, ln=True)
            except:
                # Si falla incluso con texto simplificado, usar solo alfanuméricos
                ultra_safe = "".join(c for c in chunk if c.isalnum() or c == " ")
                try:
                    pdf.cell(0, 10, ultra_safe, ln=True)
                except:
                    # Abandonar este chunk si todo falla
                    pass

        pdf.ln(10)

    # Generar PDF
    try:
        output = io.BytesIO()
        pdf.output(output)
        return output.getvalue(), "pdf"
    except Exception as e:
        logging.error(f"Error incluso en fallback: {str(e)}")
        raise e


def export_chat_to_markdown(messages):
    """
    Exporta el historial de chat a formato markdown
    con mejoras de formato y legibilidad, incluyendo información del experto
    que respondió cada mensaje
    """
    md_content = f"# {APP_IDENTITY['name']} - Historial de Conversación\n\n"
    md_content += f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # Obtener información de expertos si está disponible
    expert_info = {}
    if "assistants_config" in st.session_state:
        for expert_key, expert_data in st.session_state.assistants_config.items():
            expert_info[expert_key] = {
                "titulo": expert_data.get("titulo", "Experto"),
                "descripcion": expert_data.get("descripcion", "")
            }

    # Obtener historial de expertos si está disponible
    expert_history = []
    if "expert_history" in st.session_state:
        expert_history = st.session_state.expert_history

    # Añadir información sobre el historial de expertos
    if expert_history:
        md_content += "## Historial de Expertos\n\n"
        for entry in expert_history:
            expert_key = entry.get("expert", "")
            expert_title = expert_info.get(expert_key, {}).get("titulo", expert_key) if expert_key else "Desconocido"
            md_content += f"- **{entry.get('timestamp', '')}**: {expert_title}"
            if "reason" in entry:
                md_content += f" - *{entry.get('reason', '')}*"
            md_content += "\n"
        md_content += "\n\n"

    # Obtener el experto predeterminado
    default_expert = "asistente_virtual"
    if "assistants_config" in st.session_state and default_expert not in expert_info:
        # Si no existe el asistente_virtual, usar el primer experto disponible
        if expert_info:
            default_expert = list(expert_info.keys())[0]

    # Crear un mapa de mensajes a expertos basado en el historial
    # Esto nos permitirá saber qué experto estaba activo en cada momento
    expert_timeline = []
    if expert_history:
        # Ordenar el historial por timestamp (asumiendo que ya está ordenado, pero por si acaso)
        for entry in expert_history:
            if "timestamp" in entry and "expert" in entry:
                try:
                    # Convertir timestamp a datetime para comparación
                    # Formato esperado: "08:41:57 AM"
                    time_str = entry.get("timestamp", "")
                    expert_key = entry.get("expert", default_expert)

                    # Añadir a la línea de tiempo
                    expert_timeline.append({
                        "timestamp": time_str,
                        "expert": expert_key
                    })
                except Exception as e:
                    logging.warning(f"Error procesando entrada de historial: {str(e)}")

    # Si no hay historial, usar el experto actual
    if not expert_timeline and "current_expert" in st.session_state:
        expert_timeline.append({
            "timestamp": "00:00:00",  # Tiempo ficticio anterior a cualquier mensaje
            "expert": st.session_state.current_expert
        })

    # Si aún no hay timeline, usar el experto predeterminado
    if not expert_timeline:
        expert_timeline.append({
            "timestamp": "00:00:00",
            "expert": default_expert
        })

    # Procesar mensajes con información de experto correcta
    message_index = 0
    user_message_count = 0

    for msg in messages:
        if msg["role"] == "user":
            # Contar mensajes de usuario para sincronizar con respuestas
            user_message_count += 1
            role = "Usuario"
            md_content += f"## {role}\n\n{msg['content']}\n\n"
        else:
            # Para mensajes del asistente, determinar qué experto respondió
            # Asumimos que cada mensaje del asistente corresponde al experto activo en ese momento
            # Usamos el índice del mensaje para determinar el experto

            # Por defecto, usar el último experto en la línea de tiempo
            expert_key = expert_timeline[-1]["expert"] if expert_timeline else default_expert

            # Si hay suficientes entradas en el historial, usar el experto correspondiente
            # Restamos 1 porque el primer mensaje del asistente corresponde al experto inicial
            if user_message_count - 1 < len(expert_timeline):
                expert_key = expert_timeline[max(0, user_message_count - 1)]["expert"]

            # Obtener información del experto
            expert_title = expert_info.get(expert_key, {}).get("titulo", expert_key) if expert_key else APP_IDENTITY["name"]
            expert_desc = expert_info.get(expert_key, {}).get("descripcion", "")

            md_content += f"## {expert_title}\n\n"

            # Añadir descripción del experto si está disponible
            if expert_desc:
                md_content += f"*{expert_desc}*\n\n"

            md_content += f"{msg['content']}\n\n"

        md_content += "---\n\n"  # Separador para mejorar legibilidad
        message_index += 1

    # Añadir sección de archivos adjuntos si existen
    has_attachments = False
    attachment_files = []

    # Verificar si hay archivos adjuntos en la sesión
    if "uploaded_files" in st.session_state:
        # Verificar si uploaded_files es una lista de objetos o una lista de nombres
        if st.session_state.uploaded_files:
            has_attachments = True

            # Procesar cada archivo
            for file_item in st.session_state.uploaded_files:
                # Si es un objeto de archivo
                if hasattr(file_item, "name"):
                    file_info = {
                        "name": file_item.name,
                        "source": "session"
                    }
                    # Añadir información adicional si está disponible
                    if hasattr(file_item, "size"):
                        file_info["size"] = file_item.size
                    if hasattr(file_item, "type"):
                        file_info["type"] = file_item.type
                    attachment_files.append(file_info)
                # Si es un string (nombre de archivo)
                elif isinstance(file_item, str):
                    attachment_files.append({
                        "name": file_item,
                        "source": "session"
                    })

    # Verificar si hay menciones de archivos adjuntos en los mensajes
    for msg in messages:
        if msg["role"] == "user":
            content = msg["content"]

            # Buscar menciones de archivos adjuntos en formato "*Archivo adjunto: nombre*"
            if "*Archivo adjunto:" in content:
                start_idx = content.find("*Archivo adjunto:")
                if start_idx != -1:
                    end_idx = content.find("*", start_idx + 1)
                    if end_idx != -1:
                        file_mention = content[start_idx+18:end_idx].strip()
                        # Verificar si ya está en la lista
                        if not any(f["name"] == file_mention for f in attachment_files):
                            attachment_files.append({
                                "name": file_mention,
                                "source": "mention"
                            })

            # Buscar menciones de archivos adjuntos en formato "*Archivo adjunto para análisis: nombre*"
            if "*Archivo adjunto para análisis:" in content:
                start_idx = content.find("*Archivo adjunto para análisis:")
                if start_idx != -1:
                    end_idx = content.find("*", start_idx + 1)
                    if end_idx != -1:
                        file_mention = content[start_idx+32:end_idx].strip()
                        # Verificar si ya está en la lista
                        if not any(f["name"] == file_mention for f in attachment_files):
                            attachment_files.append({
                                "name": file_mention,
                                "source": "mention"
                            })

    # Si se encontraron archivos adjuntos, añadirlos a la sección
    if attachment_files:
        md_content += "## Archivos Adjuntos\n\n"
        for file_info in attachment_files:
            md_content += f"- **{file_info['name']}**"

            # Añadir información adicional si está disponible
            if "source" in file_info and file_info["source"] == "mention":
                md_content += " (mencionado en la conversación)"

            if "size" in file_info:
                size_kb = file_info["size"] / 1024
                md_content += f"\n  - Tamaño: {size_kb:.2f} KB"

            if "type" in file_info:
                md_content += f"\n  - Tipo: {file_info['type']}"

            md_content += "\n"

        md_content += "\n"

    return md_content


# Definición de formatos permitidos y sus extensiones
ALLOWED_FILE_FORMATS = {
    "PDF": [".pdf"],
    "Imagen": [".jpg", ".jpeg", ".png"],
    "Texto": [".txt"],
    "Markdown": [".md"],
    # "Word": [".docx"]  # Eliminado porque la API de Mistral no acepta documentos Word en base64
}

# Lista plana de todas las extensiones permitidas
ALLOWED_EXTENSIONS = [ext for exts in ALLOWED_FILE_FORMATS.values() for ext in exts]


# Funciones de OCR con Mistral
@handle_error(max_retries=1)
def validate_file_format(file):
    """
    Valida que el archivo tenga un formato permitido y que su contenido
    sea consistente con la extensión declarada.

    Parámetros:
        file: Objeto de archivo cargado por el usuario mediante Streamlit

    Retorno:
        tuple: (es_válido, tipo_documento, mensaje_error)
    """
    file_type = None

    # Verificar que el archivo tenga nombre
    if not hasattr(file, "name"):
        return False, None, "El archivo no tiene nombre"

    # Obtener extensión y verificar que esté permitida
    file_name = file.name.lower()
    file_ext = os.path.splitext(file_name)[1]

    if file_ext not in ALLOWED_EXTENSIONS:
        allowed_exts = ", ".join(ALLOWED_EXTENSIONS)
        return False, None, f"Formato de archivo no permitido. Use: {allowed_exts}"

    # Determinar el tipo de documento según la extensión
    for doc_type, extensions in ALLOWED_FILE_FORMATS.items():
        if file_ext in extensions:
            file_type = doc_type
            break

    # Verificar contenido según el tipo de archivo
    try:
        # Guardar posición del cursor
        position = file.tell()

        # Verificar contenido según tipo
        if file_type == "PDF":
            # Verificar firma de PDF
            header = file.read(8)
            file.seek(position)  # Restaurar posición

            if not header.startswith(b"%PDF"):
                return False, None, "El archivo no es un PDF válido"

        elif file_type == "Imagen":
            # Intentar abrir como imagen
            try:
                img = Image.open(file)
                img.verify()  # Verificar que la imagen sea válida
                file.seek(position)  # Restaurar posición
            except Exception as e:
                file.seek(position)  # Restaurar posición
                return False, None, f"El archivo no es una imagen válida: {str(e)}"

        elif file_type == "Markdown":
            # Verificar que el archivo sea texto y contenga sintaxis markdown
            try:
                # Leer los primeros 1024 bytes para verificar que sea texto
                content = file.read(1024).decode('utf-8', errors='ignore')
                file.seek(position)  # Restaurar posición

                # Verificación básica de sintaxis markdown (encabezados, listas, etc.)
                has_markdown = False
                if (
                    re.search(r'^#{1,6}\s+', content, re.MULTILINE) or  # Encabezados
                    re.search(r'^[-*+]\s+', content, re.MULTILINE) or   # Listas
                    re.search(r'^\d+\.\s+', content, re.MULTILINE) or   # Listas numeradas
                    re.search(r'\*\*.*?\*\*', content) or               # Negrita
                    re.search(r'_.*?_', content) or                     # Cursiva
                    re.search(r'\[.*?\]\(.*?\)', content) or            # Enlaces
                    re.search(r'```', content) or                       # Bloques de código
                    re.search(r'>\s+', content, re.MULTILINE)           # Citas
                ):
                    has_markdown = True

                # Si no tiene sintaxis markdown pero es un archivo .md, lo aceptamos de todas formas
                if not has_markdown:
                    logging.info(f"El archivo {file.name} tiene extensión .md pero no se detectó sintaxis markdown clara")
            except Exception as e:
                file.seek(position)  # Restaurar posición
                return False, None, f"Error al validar archivo Markdown: {str(e)}"

        # Eliminada la validación de archivos Word

    except Exception as e:
        # Restaurar posición en caso de error
        try:
            file.seek(position)
        except:
            pass
        return False, None, f"Error validando el archivo: {str(e)}"

    # Si llegamos aquí, el archivo es válido
    return True, file_type, None


@handle_error(max_retries=1)
def detect_document_type(file):
    """
    Detecta automáticamente si un archivo es un PDF o una imagen
    con múltiples verificaciones para mayor precisión

    Parámetros:
        file: Objeto de archivo cargado por el usuario mediante Streamlit

    Retorno:
        string: Tipo de documento detectado ("PDF" o "Imagen")
    """
    # 1. Verificar por MIME type
    if hasattr(file, "type"):
        mime_type = file.type
        if mime_type.startswith("application/pdf"):
            return "PDF"
        elif mime_type.startswith("image/"):
            return "Imagen"
        elif mime_type in ["text/markdown", "text/x-markdown"]:
            return "Markdown"

    # 2. Verificar por extensión del nombre
    if hasattr(file, "name"):
        name = file.name.lower()
        if name.endswith(".pdf"):
            return "PDF"
        elif name.endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp")):
            return "Imagen"
        elif name.endswith(".md"):
            return "Markdown"

    # 3. Verificar contenido con análisis de bytes
    try:
        # Guardar posición del cursor
        position = file.tell()
        # Leer los primeros bytes
        header = file.read(8)
        file.seek(position)  # Restaurar posición

        # Verificar firmas de archivo comunes
        if header.startswith(b"%PDF"):
            return "PDF"
        elif header.startswith(b"\x89PNG") or header.startswith(b"\xff\xd8"):
            return "Imagen"
    except:
        pass

    # 4. Intentar abrir como imagen (último recurso)
    try:
        Image.open(file)
        file.seek(0)  # Restaurar el puntero
        return "Imagen"
    except:
        file.seek(0)  # Restaurar el puntero

    # Asumir PDF por defecto
    return "PDF"


@handle_error(max_retries=1)
def prepare_image_for_ocr(file_data):
    """
    Prepara una imagen para ser procesada con OCR,
    optimizando formato y calidad para mejorar resultados

    Parámetros:
        file_data: Datos binarios de la imagen

    Retorno:
        tuple: (datos_optimizados, mime_type)
    """
    try:
        # Abrir la imagen con PIL
        img = Image.open(BytesIO(file_data))

        # Optimizaciones avanzadas para OCR
        # 1. Convertir a escala de grises si tiene más de un canal
        if img.mode != "L" and img.mode != "1":
            img = img.convert("L")

        # 2. Ajustar tamaño si es muy grande (límite 4000px)
        max_dimension = 4000
        if img.width > max_dimension or img.height > max_dimension:
            ratio = min(max_dimension / img.width, max_dimension / img.height)
            new_width = int(img.width * ratio)
            new_height = int(img.height * ratio)
            img = img.resize((new_width, new_height), Image.LANCZOS)

        # 3. Evaluar y determinar mejor formato
        # JPEG para imágenes fotográficas, PNG para documentos/texto
        save_format = "JPEG"
        save_quality = 95

        # Detectar si es más probable que sea un documento (blanco/negro predominante)
        histogram = img.histogram()
        if img.mode == "L" and (histogram[0] + histogram[-1]) > sum(histogram) * 0.8:
            save_format = "PNG"

        # 4. Guardar con parámetros optimizados
        buffer = BytesIO()
        if save_format == "JPEG":
            img.save(buffer, format=save_format, quality=save_quality, optimize=True)
        else:
            img.save(buffer, format=save_format, optimize=True)

        buffer.seek(0)
        return buffer.read(), f"image/{save_format.lower()}"

    except Exception as e:
        logging.warning(f"Optimización de imagen fallida: {str(e)}")
        return file_data, "image/jpeg"  # Formato por defecto


@handle_error(max_retries=1)
def process_markdown_file(file_data):
    """
    Procesa un archivo Markdown y extrae su contenido como texto.

    Parámetros:
        file_data: Datos binarios del archivo Markdown

    Retorno:
        dict: Diccionario con el texto extraído
    """
    try:
        # Decodificar el contenido del archivo
        content = file_data.decode('utf-8', errors='ignore')

        # Devolver el contenido como texto
        return {
            "text": content,
            "format": "markdown"
        }
    except Exception as e:
        logging.error(f"Error procesando archivo Markdown: {str(e)}")
        return {
            "text": f"Error al procesar el archivo Markdown: {str(e)}",
            "format": "error"
        }


@handle_error(max_retries=1)
def extract_text_from_ocr_response(response):
    """
    Extrae texto de diferentes formatos de respuesta OCR
    con soporte para múltiples estructuras de datos

    Parámetros:
        response: Respuesta JSON del servicio OCR

    Retorno:
        dict: Diccionario con el texto extraído
    """
    # Registro para diagnóstico
    logging.info(f"Procesando respuesta OCR de tipo: {type(response)}")

    # Caso 1: Si hay páginas con markdown (formato preferido)
    if "pages" in response and isinstance(response["pages"], list):
        pages = response["pages"]
        if pages and "markdown" in pages[0]:
            markdown_text = "\n\n".join(page.get("markdown", "") for page in pages)
            if markdown_text.strip():
                return {"text": markdown_text, "format": "markdown"}

    # Caso 2: Si hay un texto plano en la respuesta
    if "text" in response:
        return {"text": response["text"], "format": "text"}

    # Caso 3: Si hay elementos estructurados
    if "elements" in response:
        elements = response["elements"]
        if isinstance(elements, list):
            text_parts = []
            for element in elements:
                if "text" in element:
                    text_parts.append(element["text"])
            return {"text": "\n".join(text_parts), "format": "elements"}

    # Caso 4: Si hay un campo 'content' principal
    if "content" in response:
        return {"text": response["content"], "format": "content"}

    # Caso 5: Extracción recursiva de todos los campos de texto
    try:
        response_str = json.dumps(response, indent=2)
        # Si la respuesta es muy grande, limitar extracción
        if len(response_str) > 10000:
            response_str = response_str[:10000] + "... [truncado]"

        extracted_text = extract_all_text_fields(response)
        if extracted_text:
            return {"text": extracted_text, "format": "extracted"}

        return {
            "text": "No se pudo encontrar texto estructurado en la respuesta OCR. Vea los detalles técnicos.",
            "format": "unknown",
            "raw_response": response_str,
        }
    except Exception as e:
        logging.error(f"Error al procesar respuesta OCR: {str(e)}")
        return {"error": f"Error al procesar la respuesta: {str(e)}"}


@handle_error(max_retries=0)
def extract_all_text_fields(data, prefix="", max_depth=5, current_depth=0):
    """
    Función recursiva optimizada para extraer todos los campos de texto
    de un diccionario anidado con límites de profundidad

    Parámetros:
        data: Diccionario o lista de datos
        prefix: Prefijo para la ruta de acceso (uso recursivo)
        max_depth: Profundidad máxima de recursión
        current_depth: Profundidad actual (uso recursivo)

    Retorno:
        string: Texto extraído
    """
    # Evitar recursión infinita
    if current_depth > max_depth:
        return []

    result = []

    if isinstance(data, dict):
        for key, value in data.items():
            new_prefix = f"{prefix}.{key}" if prefix else key

            if isinstance(value, str) and len(value) > 1:
                result.append(f"{new_prefix}: {value}")
            elif (
                isinstance(value, (dict, list)) and value
            ):  # Solo recursión si hay contenido
                child_results = extract_all_text_fields(
                    value, new_prefix, max_depth, current_depth + 1
                )
                result.extend(child_results)

    elif isinstance(data, list):
        # Limitar número de elementos procesados en listas muy grandes
        max_items = 20
        for i, item in enumerate(data[:max_items]):
            new_prefix = f"{prefix}[{i}]"
            if isinstance(item, (dict, list)) and item:
                child_results = extract_all_text_fields(
                    item, new_prefix, max_depth, current_depth + 1
                )
                result.extend(child_results)
            elif isinstance(item, str) and len(item) > 1:
                result.append(f"{new_prefix}: {item}")

        # Indicar si se truncó la lista
        if len(data) > max_items:
            result.append(
                f"{prefix}: [... {len(data) - max_items} elementos adicionales omitidos]"
            )

    return "\n".join(result)


@handle_error(max_retries=1)
def process_document_with_mistral_ocr(api_key, file_bytes, file_type, file_name):
    """
    Procesa un documento con OCR de Mistral
    con sistema de recuperación ante fallos

    Parámetros:
        api_key: API key de Mistral
        file_bytes: Bytes del archivo
        file_type: Tipo de archivo ("PDF", "Imagen", "Texto" o "Word")
        file_name: Nombre del archivo

    Retorno:
        dict: Texto extraído del documento
    """
    job_id = str(uuid.uuid4())
    logging.info(f"Procesando documento {file_name} con Mistral OCR (ID: {job_id})")

    # Mostrar estado
    with st.status(f"Procesando documento {file_name}...", expanded=True) as status:
        try:
            status.update(label="Preparando documento para OCR...", state="running")

            # Guardar una copia del archivo para depuración
            debug_dir = os.path.join(
                tempfile.gettempdir(), f"{APP_IDENTITY['document_prefix']}_debug"
            )
            os.makedirs(debug_dir, exist_ok=True)
            debug_file_path = os.path.join(debug_dir, f"debug_{job_id}_{file_name}")

            with open(debug_file_path, "wb") as f:
                f.write(file_bytes)

            logging.info(f"Archivo de depuración guardado en: {debug_file_path}")

            # Sistema de procesamiento con verificación según tipo
            if file_type == "PDF":
                # Verificar que el PDF sea válido
                try:
                    import PyPDF2

                    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                    page_count = len(reader.pages)
                    sample_text = ""
                    if page_count > 0:
                        sample_text = reader.pages[0].extract_text()[:100]
                    logging.info(
                        f"PDF válido con {page_count} páginas. Muestra: {sample_text}"
                    )

                    # Codificar PDF en base64
                    encoded_file = base64.b64encode(file_bytes).decode("utf-8")
                    document = {
                        "type": "document_url",
                        "document_url": f"data:application/pdf;base64,{encoded_file}",
                    }
                except Exception as e:
                    logging.error(f"Error al validar PDF: {str(e)}")
                    status.update(
                        label=f"Error al validar PDF: {str(e)}", state="error"
                    )
                    return {"error": f"El archivo no es un PDF válido: {str(e)}"}
            elif file_type == "Imagen":
                # Optimizar imagen para mejores resultados
                try:
                    optimized_bytes, mime_type = prepare_image_for_ocr(file_bytes)

                    # Codificar en base64
                    encoded_file = base64.b64encode(optimized_bytes).decode("utf-8")
                    document = {
                        "type": "image_url",
                        "image_url": f"data:{mime_type};base64,{encoded_file}",
                    }
                except Exception as e:
                    logging.error(f"Error al procesar imagen: {str(e)}")
                    status.update(
                        label=f"Error al procesar imagen: {str(e)}", state="error"
                    )
                    return {"error": f"El archivo no es una imagen válida: {str(e)}"}
            elif file_type == "Texto":
                # Para archivos de texto, extraer contenido directamente
                try:
                    # Intentar leer con diferentes codificaciones
                    text_content = None
                    try:
                        text_content = file_bytes.decode("utf-8")
                    except UnicodeDecodeError:
                        # Intentar con otras codificaciones comunes
                        for encoding in ["latin-1", "cp1252", "iso-8859-1"]:
                            try:
                                text_content = file_bytes.decode(encoding)
                                break
                            except UnicodeDecodeError:
                                continue

                    # Si pudimos decodificar el texto, devolverlo
                    if text_content:
                        logging.info(f"Archivo de texto {file_name} decodificado correctamente")
                        return {"text": text_content, "format": "text"}

                    # Si llegamos aquí, no pudimos decodificar el texto
                    # Intentar enviar como documento plano
                    status.update(
                        label=f"Convirtiendo documento de texto {file_name} para OCR...",
                        state="running",
                    )

                    # Codificar en base64 y enviar como documento
                    encoded_file = base64.b64encode(file_bytes).decode("utf-8")
                    document = {
                        "type": "document_url",
                        "document_url": f"data:text/plain;base64,{encoded_file}",
                    }
                except Exception as e:
                    logging.error(f"Error al procesar documento de texto: {str(e)}")
                    status.update(
                        label=f"Error al procesar documento: {str(e)}", state="error"
                    )
                    return {"error": f"Error al procesar documento de texto: {str(e)}"}
            else:
                # Tipo de documento no soportado
                error_msg = f"Tipo de documento no soportado: {file_type}"
                logging.error(error_msg)
                status.update(label=error_msg, state="error")
                return {"error": error_msg}

            status.update(
                label="Enviando documento a la API de Mistral...", state="running"
            )

            # Configurar los headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }

            # Preparar payload
            payload = {"model": "mistral-ocr-latest", "document": document}

            # Guardar payload para depuración (excluyendo contenido base64 por tamaño)
            debug_payload = {
                "model": payload["model"],
                "document": {
                    "type": payload["document"]["type"],
                    "content_size": len(encoded_file),
                    "content_format": "base64",
                },
            }
            logging.info(f"Payload para OCR: {json.dumps(debug_payload)}")

            # Sistema de retry interno para la API de Mistral
            max_retries = 2
            retry_delay = 2
            last_error = None

            for retry in range(max_retries + 1):
                try:
                    # Hacer la solicitud a Mistral OCR API
                    response = requests.post(
                        "https://api.mistral.ai/v1/ocr",
                        json=payload,
                        headers=headers,
                        timeout=90,  # Timeout ampliado para documentos grandes
                    )

                    logging.info(
                        f"Respuesta de OCR API - Estado: {response.status_code}"
                    )

                    if response.status_code == 200:
                        try:
                            result = response.json()
                            # Guardar respuesta para depuración
                            with open(
                                os.path.join(
                                    debug_dir, f"response_{job_id}_{file_name}.json"
                                ),
                                "w",
                            ) as f:
                                json.dump(result, f, indent=2)

                            status.update(
                                label=f"Documento {file_name} procesado exitosamente",
                                state="complete",
                            )

                            # Verificar existencia de contenido
                            if not result or (isinstance(result, dict) and not result):
                                return {
                                    "error": "La API no devolvió contenido",
                                    "raw_response": str(result),
                                }

                            # Extraer texto de la respuesta
                            extracted_content = extract_text_from_ocr_response(result)

                            if "error" in extracted_content:
                                status.update(
                                    label=f"Error al extraer texto: {extracted_content['error']}",
                                    state="error",
                                )
                                return {
                                    "error": extracted_content["error"],
                                    "raw_response": result,
                                }

                            return extracted_content
                        except Exception as e:
                            error_message = (
                                f"Error al procesar respuesta JSON: {str(e)}"
                            )
                            logging.error(error_message)
                            # Guardar respuesta cruda para depuración
                            with open(
                                os.path.join(
                                    debug_dir, f"raw_response_{job_id}_{file_name}.txt"
                                ),
                                "w",
                            ) as f:
                                f.write(response.text[:10000])  # Limitar tamaño
                            status.update(label=error_message, state="error")
                            last_error = e
                    elif response.status_code == 429:  # Rate limit
                        if retry < max_retries:
                            wait_time = retry_delay * (retry + 1)
                            logging.warning(
                                f"Rate limit alcanzado. Esperando {wait_time}s antes de reintentar..."
                            )
                            status.update(
                                label=f"Límite de tasa alcanzado. Reintentando en {wait_time}s...",
                                state="running",
                            )
                            time.sleep(wait_time)
                            continue
                        else:
                            error_message = "Límite de tasa alcanzado. No se pudo procesar después de reintentos."
                            logging.error(error_message)
                            status.update(label=error_message, state="error")
                            return {
                                "error": error_message,
                                "raw_response": response.text,
                            }
                    else:
                        error_message = f"Error en API OCR ({response.status_code}): {response.text[:500]}"
                        logging.error(error_message)
                        status.update(label=f"Error: {error_message}", state="error")
                        last_error = Exception(error_message)
                        break
                except requests.exceptions.Timeout:
                    if retry < max_retries:
                        wait_time = retry_delay * (retry + 1)
                        logging.warning(
                            f"Timeout al contactar API. Esperando {wait_time}s antes de reintentar..."
                        )
                        status.update(
                            label=f"Timeout. Reintentando en {wait_time}s...",
                            state="running",
                        )
                        time.sleep(wait_time)
                    else:
                        error_message = (
                            "Timeout al contactar API después de múltiples intentos."
                        )
                        logging.error(error_message)
                        status.update(label=error_message, state="error")
                        return {"error": error_message}
                except Exception as e:
                    if retry < max_retries:
                        wait_time = retry_delay * (retry + 1)
                        logging.warning(
                            f"Error: {str(e)}. Esperando {wait_time}s antes de reintentar..."
                        )
                        status.update(
                            label=f"Error. Reintentando en {wait_time}s...",
                            state="running",
                        )
                        time.sleep(wait_time)
                    else:
                        error_message = f"Error al procesar documento: {str(e)}"
                        logging.error(error_message)
                        status.update(label=f"Error: {error_message}", state="error")
                        last_error = e
                        break

            # Si llegamos aquí después de reintentos, devolver último error
            return {
                "error": f"Error después de reintentos: {str(last_error)}",
                "details": traceback.format_exc(),
            }

        except Exception as e:
            error_message = f"Error general al procesar documento: {str(e)}"
            logging.error(error_message)
            logging.error(traceback.format_exc())
            status.update(label=f"Error: {error_message}", state="error")
            return {"error": error_message}


# Función segura para gestionar el contexto de documentos
@handle_error(max_retries=0)
def manage_document_context():
    """
    Permite al usuario gestionar qué documentos mantener en el contexto actual
    con manejo seguro de actualización de estado
    """
    if "document_contents" in st.session_state and st.session_state.document_contents:
        st.write("Documentos en contexto actual:")

        # Crear checkboxes para cada documento
        docs_to_keep = {}
        for doc_name in st.session_state.document_contents:
            docs_to_keep[doc_name] = st.checkbox(
                f"{doc_name}", value=True, key=f"keep_{doc_name}"
            )

        # Botón para aplicar cambios
        if st.button("Actualizar contexto", key="update_context"):
            # Eliminar documentos no seleccionados
            docs_to_remove = [doc for doc, keep in docs_to_keep.items() if not keep]
            if docs_to_remove:
                for doc in docs_to_remove:
                    if doc in st.session_state.document_contents:
                        del st.session_state.document_contents[doc]
                    if doc in st.session_state.uploaded_files:
                        st.session_state.uploaded_files.remove(doc)

                st.success(
                    f"Se eliminaron {len(docs_to_remove)} documentos del contexto."
                )
                # Usar sistema seguro de reinicio
                rerun_app()
            else:
                st.info("No se seleccionaron documentos para eliminar.")
    else:
        st.info("No hay documentos cargados en el contexto actual.")


# Función para verificar el contexto de documentos
@handle_error(max_retries=0)
def verify_document_context():
    """
    Verifica que los documentos en el contexto estén correctamente procesados
    y disponibles para el asistente. También detecta y permite eliminar archivos temporales.
    """
    if "document_contents" in st.session_state and st.session_state.document_contents:
        st.write("### Verificación de documentos en contexto")

        # Detectar archivos temporales (patrones comunes)
        temp_file_patterns = ["img-", "temp", "~$", ".tmp"]
        potential_temp_files = []

        # Verificar cada documento
        for doc_name, doc_content in st.session_state.document_contents.items():
            # Verificar si parece un archivo temporal
            is_temp_file = any(pattern in doc_name.lower() for pattern in temp_file_patterns)

            if is_temp_file:
                potential_temp_files.append(doc_name)
                st.warning(f"⚠️ {doc_name}: Posible archivo temporal")

            if isinstance(doc_content, dict) and "text" in doc_content:
                text_length = len(doc_content["text"])
                format_type = doc_content.get("format", "desconocido")

                # Mostrar estado con color según el tamaño del texto
                if text_length > 1000:
                    st.success(f"✅ {doc_name}: {text_length} caracteres, formato: {format_type}")
                elif text_length > 0:
                    st.warning(f"⚠️ {doc_name}: Solo {text_length} caracteres, formato: {format_type}")
                else:
                    st.error(f"❌ {doc_name}: No se extrajo texto (0 caracteres)")
            elif isinstance(doc_content, dict) and "error" in doc_content:
                st.error(f"❌ {doc_name}: Error - {doc_content.get('error', 'Error desconocido')}")
            else:
                st.warning(f"⚠️ {doc_name}: Formato no reconocido")

        # Opción para eliminar archivos temporales si se detectaron
        if potential_temp_files:
            st.write("### Archivos temporales detectados")
            st.write("Se detectaron posibles archivos temporales que podrían no ser relevantes para el contexto:")

            # Crear checkboxes para seleccionar archivos a eliminar
            files_to_remove = {}
            for temp_file in potential_temp_files:
                files_to_remove[temp_file] = st.checkbox(
                    f"Eliminar {temp_file}", value=True, key=f"remove_temp_{temp_file}"
                )

            # Botón para eliminar archivos temporales
            if st.button("Eliminar archivos temporales seleccionados"):
                removed_count = 0
                for file_name, should_remove in files_to_remove.items():
                    if should_remove:
                        if file_name in st.session_state.document_contents:
                            del st.session_state.document_contents[file_name]
                        if file_name in st.session_state.uploaded_files:
                            st.session_state.uploaded_files.remove(file_name)
                        removed_count += 1

                if removed_count > 0:
                    st.success(f"Se eliminaron {removed_count} archivos temporales del contexto.")
                    # Usar sistema seguro de reinicio
                    rerun_app()
                else:
                    st.info("No se seleccionaron archivos para eliminar.")

        # Botón para refrescar documentos
        if st.button("Refrescar documentos en contexto"):
            st.success("Contexto de documentos actualizado")
            # Usar sistema seguro de reinicio
            rerun_app()
    else:
        st.info("No hay documentos en el contexto actual.")


# Función para inicializar un thread con OpenAI Assistants
@handle_error(max_retries=1)
def initialize_thread(client):
    """
    Inicializa un nuevo thread de conversación
    con verificación de éxito
    """
    try:
        thread = client.beta.threads.create()
        thread_id = thread.id
        logging.info(f"Thread creado: {thread_id}")

        # Verificar que el thread se creó correctamente
        test_thread = client.beta.threads.retrieve(thread_id=thread_id)
        if not test_thread or not hasattr(test_thread, "id"):
            raise Exception("El thread se creó pero no se puede recuperar")

        return thread_id
    except Exception as e:
        logging.error(f"Error creando thread: {str(e)}")
        st.error("No se pudo inicializar la conversación con el asistente")
        return None


# Función para procesar mensajes del asistente
@handle_error(max_retries=1)
def process_message_with_citations(message):
    """
    Extrae y formatea el texto del mensaje del asistente con citas adecuadas,
    manejando diferentes formatos de respuesta
    """
    try:
        # Verificar que el mensaje tenga contenido
        if not hasattr(message, "content") or not message.content:
            return "No se pudo procesar el mensaje"

        # Procesar cada parte del contenido
        processed_content = ""
        for content_item in message.content:
            # Verificar tipo de contenido
            if hasattr(content_item, "text") and content_item.text:
                # Procesar texto con anotaciones si existen
                text_value = content_item.text.value
                annotations = []

                # Extraer anotaciones si existen
                if (
                    hasattr(content_item.text, "annotations")
                    and content_item.text.annotations
                ):
                    annotations = content_item.text.annotations

                    # Procesar cada anotación para formatear citas de archivos
                    if annotations:
                        # Recolectar información de citas
                        citations = []
                        for idx, annotation in enumerate(annotations):
                            # Reemplazar el texto de la anotación con un marcador de referencia
                            text_value = text_value.replace(
                                annotation.text, f"[{idx+1}]"
                            )

                            # Extraer detalles de la cita si es una cita de archivo
                            if file_citation := getattr(
                                annotation, "file_citation", None
                            ):
                                file_id = file_citation.file_id
                                # Buscar el nombre del archivo en los metadatos
                                file_name = "Documento de referencia"
                                if (
                                    "file_metadata" in st.session_state
                                    and file_id in st.session_state.file_metadata
                                ):
                                    file_name = st.session_state.file_metadata[file_id][
                                        "name"
                                    ]

                                citations.append(f"[{idx+1}] Fuente: {file_name}")

                        # Añadir las citas al final del texto procesado si existen
                        if citations:
                            text_value += "\n\n--- Referencias: ---\n" + "\n".join(
                                citations
                            )

                processed_content += text_value
            else:
                # Si no es texto, añadimos una representación genérica
                processed_content += str(content_item)

        return processed_content
    except Exception as e:
        logging.error(f"Error procesando mensaje: {str(e)}")
        logging.error(traceback.format_exc())
        return "Error al procesar la respuesta del asistente"


# Función para enviar mensaje a OpenAI con contexto de documentos
@handle_error(max_retries=1)
def send_message_with_document_context(
    client, thread_id, assistant_id, prompt, current_doc_contents=None
):
    """
    Envía un mensaje al asistente incluyendo el contexto de todos los documentos disponibles
    con manejo mejorado de errores y reintentos
    """
    try:
        # Construir el mensaje que incluirá el contexto del documento si existe
        full_prompt = prompt

        # Combinar documentos actuales con documentos previamente procesados
        all_doc_contents = {}

        # Añadir documentos existentes en la sesión
        if "document_contents" in st.session_state:
            all_doc_contents.update(st.session_state.document_contents)

        # Añadir documentos recién procesados, que pueden sobrescribir los anteriores
        if current_doc_contents and isinstance(current_doc_contents, dict):
            all_doc_contents.update(current_doc_contents)
            # Actualizar la sesión con los nuevos documentos
            if "document_contents" not in st.session_state:
                st.session_state.document_contents = {}
            st.session_state.document_contents.update(current_doc_contents)

        # Si hay contenido de documentos, añadirlo al prompt
        if all_doc_contents and len(all_doc_contents) > 0:
            document_context = "\n\n### Contexto de documentos procesados:\n\n"

            for doc_name, doc_content in all_doc_contents.items():
                # Extraer el texto del documento procesado por OCR
                if isinstance(doc_content, dict):
                    if "text" in doc_content:
                        # Limitamos el contenido para no exceder el contexto de OpenAI
                        doc_text = (
                            doc_content["text"][:5000] + "..."
                            if len(doc_content["text"]) > 5000
                            else doc_content["text"]
                        )
                        document_context += (
                            f"-- Documento: {doc_name} --\n{doc_text}\n\n"
                        )
                    elif "error" in doc_content and "raw_response" in doc_content:
                        # Intentar extraer texto de la respuesta cruda si está disponible
                        raw_response = doc_content["raw_response"]
                        if isinstance(raw_response, dict) and "text" in raw_response:
                            doc_text = (
                                raw_response["text"][:5000] + "..."
                                if len(raw_response["text"]) > 5000
                                else raw_response["text"]
                            )
                            document_context += (
                                f"-- Documento: {doc_name} --\n{doc_text}\n\n"
                            )
                        else:
                            document_context += f"-- Documento: {doc_name} -- (Error al extraer texto: {doc_content['error']})\n\n"
                    else:
                        document_context += f"-- Documento: {doc_name} -- (No se pudo extraer texto)\n\n"
                else:
                    document_context += (
                        f"-- Documento: {doc_name} -- (Formato no reconocido)\n\n"
                    )

            # Verificar si hay contenido real antes de añadirlo al prompt
            if len(document_context) > 60:  # Más que solo el encabezado
                full_prompt = f"{prompt}\n\n{document_context}"
                logging.info(
                    f"Prompt enriquecido con contexto de {len(all_doc_contents)} documentos. Tamaño total: {len(full_prompt)} caracteres"
                )
            else:
                logging.warning("No se pudo extraer texto útil de los documentos")

        # Crear mensaje con el prompt completo (con sistema de retry)
        message = None
        for attempt in range(2):
            try:
                message = client.beta.threads.messages.create(
                    thread_id=thread_id, role="user", content=full_prompt
                )
                break
            except Exception as e:
                if attempt == 0:
                    logging.warning(
                        f"Error al crear mensaje (intento 1): {str(e)}. Reintentando..."
                    )
                    time.sleep(2)
                else:
                    raise Exception(f"Error al crear mensaje: {str(e)}")

        if not message:
            raise Exception("No se pudo crear el mensaje después de reintentos")

        # Crear la ejecución
        run = None
        for attempt in range(2):
            try:
                run = client.beta.threads.runs.create(
                    thread_id=thread_id, assistant_id=assistant_id
                )
                break
            except Exception as e:
                if attempt == 0:
                    logging.warning(
                        f"Error al crear ejecución (intento 1): {str(e)}. Reintentando..."
                    )
                    time.sleep(2)
                else:
                    raise Exception(f"Error al crear ejecución: {str(e)}")

        if not run:
            raise Exception("No se pudo iniciar la ejecución después de reintentos")

        # Esperar a que se complete la ejecución
        with st.status(
            "Analizando consulta y procesando información...", expanded=True
        ) as status:
            run_counter = 0
            max_run_time = 120  # Tiempo máximo de espera (2 minutos)
            start_time = time.time()

            while run.status not in ["completed", "failed", "cancelled", "expired"]:
                run_counter += 1
                time.sleep(1)

                # Verificar timeout
                elapsed_time = time.time() - start_time
                if elapsed_time > max_run_time:
                    status.update(
                        label="La operación está tomando demasiado tiempo. Intente nuevamente.",
                        state="error",
                    )
                    logging.error(
                        f"Timeout después de {max_run_time}s esperando completar ejecución."
                    )
                    return None

                # Actualizar el estado cada 2 segundos para no sobrecargar la API
                if run_counter % 2 == 0:
                    try:
                        run = client.beta.threads.runs.retrieve(
                            thread_id=thread_id, run_id=run.id
                        )
                    except Exception as e:
                        logging.warning(
                            f"Error al recuperar estado de ejecución: {str(e)}"
                        )
                        # Continuar intentando, podría ser un error temporal

                # Mostrar mensajes según el estado
                if run.status == "in_progress":
                    status.update(
                        label="Procesando consulta y analizando documentos...",
                        state="running",
                    )
                elif run.status == "requires_action":
                    status.update(
                        label="Realizando acciones requeridas...", state="running"
                    )

                # Manejar errores
                if run.status == "failed":
                    error_msg = f"Error en la ejecución: {getattr(run, 'last_error', 'Desconocido')}"
                    logging.error(error_msg)
                    status.update(label="Error en el procesamiento", state="error")
                    return None

            # Actualizar estado final
            if run.status == "completed":
                status.update(label="Análisis completado", state="complete")
            else:
                status.update(label=f"Estado final: {run.status}", state="error")

        # Recuperar mensajes agregados por el asistente
        if run.status == "completed":
            try:
                messages = client.beta.threads.messages.list(thread_id=thread_id)

                # Buscar el mensaje más reciente del asistente
                for message in messages.data:
                    if message.role == "assistant" and not any(
                        msg["role"] == "assistant" and msg.get("id") == message.id
                        for msg in st.session_state.messages
                    ):
                        full_response = process_message_with_citations(message)
                        return {
                            "role": "assistant",
                            "content": full_response,
                            "id": message.id,
                        }

                # Si no se encontró un mensaje nuevo
                logging.warning("No se encontraron nuevos mensajes del asistente")
                return None
            except Exception as e:
                logging.error(f"Error al recuperar mensajes: {str(e)}")
                return None

        return None
    except Exception as e:
        logging.error(f"Error en comunicación con OpenAI: {str(e)}")
        logging.error(traceback.format_exc())
        st.error(
            "Ocurrió un error al comunicarse con el asistente. Por favor, intente nuevamente."
        )
        return None


# Función para limpiar la sesión actual
@handle_error(max_retries=0)
def clean_current_session():
    """
    Limpia todos los recursos de la sesión actual
    con verificación de resultados
    """
    try:
        resources_cleaned = {
            "documents": 0,
            "messages": (
                len(st.session_state.messages) if "messages" in st.session_state else 0
            ),
        }

        # Limpiar documentos procesados
        if "document_contents" in st.session_state:
            resources_cleaned["documents"] = len(st.session_state.document_contents)
            st.session_state.document_contents = {}

        # Limpiar lista de archivos
        if "uploaded_files" in st.session_state:
            st.session_state.uploaded_files = []

        # Limpiar historial de mensajes
        if "messages" in st.session_state:
            st.session_state.messages = []

        # Limpiar otros estados relacionados con documentos
        for key in ["file_metadata"]:
            if key in st.session_state:
                st.session_state[key] = {}

        # Verificar limpieza exitosa
        clean_success = True
        if (
            "document_contents" in st.session_state
            and st.session_state.document_contents
        ):
            clean_success = False
        if "messages" in st.session_state and st.session_state.messages:
            clean_success = False

        if clean_success:
            logging.info(
                f"Sesión limpiada exitosamente: {resources_cleaned['documents']} documentos, {resources_cleaned['messages']} mensajes"
            )
        else:
            logging.warning(
                "Limpieza de sesión incompleta - algunos elementos persistieron"
            )

        return resources_cleaned
    except Exception as e:
        logging.error(f"Error limpiando sesión: {str(e)}")
        return {"documents": 0, "messages": 0, "error": str(e)}


# ----- FUNCIONES PARA SISTEMA DE EXPERTOS MÚLTIPLES -----

# No usamos cache_data para evitar problemas de serialización
def load_assistants_config():
    """
    Carga la configuración de asistentes desde secrets.toml
    """
    try:
        # Intentar cargar desde secrets.toml primero
        if hasattr(st, 'secrets') and 'assistants' in st.secrets:
            logging.info("Cargando configuración de asistentes desde secrets.toml")
            return st.secrets['assistants']
        else:
            # Si no está disponible en secrets, usar la configuración predefinida como fallback
            logging.warning("No se encontró configuración de asistentes en secrets.toml, usando fallback")
            return assistants_config.ASSISTANTS_CONFIG
    except Exception as e:
        logging.error(f"Error cargando configuración de asistentes: {str(e)}")
        st.error("No se pudo cargar la configuración de asistentes.")
        return {}

# ----- INICIALIZACIÓN DE ESTADO -----

# Inicializar variables de estado
if "assistants_config" not in st.session_state:
    st.session_state.assistants_config = load_assistants_config()

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

if "document_contents" not in st.session_state:
    st.session_state.document_contents = {}

if "file_metadata" not in st.session_state:
    st.session_state.file_metadata = {}

if "expert_history" not in st.session_state:
    st.session_state.expert_history = []

if "current_expert" not in st.session_state:
    # Obtener el experto predeterminado de secrets.toml o usar asistente_virtual como fallback
    default_expert = "asistente_virtual"  # Valor por defecto

    # Intentar obtener el experto predeterminado de secrets.toml
    if hasattr(st, 'secrets') and 'ASSISTANT_ID' in st.secrets:
        # Buscar el experto que coincida con el ID en secrets.toml
        assistant_id_from_secrets = st.secrets['ASSISTANT_ID']
        logging.info(f"Buscando experto con ID: {assistant_id_from_secrets}")

        # Buscar en la configuración de asistentes
        if "assistants_config" in st.session_state:
            for expert_key, expert_data in st.session_state.assistants_config.items():
                if expert_data.get('id') == assistant_id_from_secrets:
                    default_expert = expert_key
                    logging.info(f"Experto predeterminado encontrado en secrets.toml: {default_expert}")
                    break

    st.session_state.current_expert = default_expert
    # Registrar el primer experto en el historial con formato de 12 horas
    st.session_state.expert_history.append({
        "timestamp": datetime.now().strftime("%I:%M:%S %p"),
        "expert": default_expert,
        "reason": "Inicio de conversación"
    })

# ----- INICIALIZACIÓN DE INTERFAZ -----

# Título principal
st.title(f"{APP_IDENTITY['name']} {APP_IDENTITY['icon']} {APP_IDENTITY['tagline']}")

# Barra lateral con toda la información e instrucciones
with st.sidebar:
    st.title(f"{APP_IDENTITY['icon']} Configuración y Recursos")

    # Obtener API Key de OpenAI (ya cargada en os.environ)
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    # Solicitar al usuario solo si no está disponible
    if not openai_api_key or openai_api_key.startswith('sk-your-'):
        openai_api_key = st.text_input(
            "API Key de OpenAI", type="password", help="Ingrese su API Key de OpenAI"
        )
        if openai_api_key and not openai_api_key.startswith('sk-your-'):
            os.environ["OPENAI_API_KEY"] = openai_api_key
            logging.info("Clave API de OpenAI proporcionada por el usuario")

    # Obtener API Key de Mistral (ya cargada en os.environ)
    mistral_api_key = os.environ.get("MISTRAL_API_KEY")

    # Solicitar al usuario solo si no está disponible
    if not mistral_api_key or mistral_api_key.startswith('your-'):
        mistral_api_key = st.text_input(
            "API Key de Mistral",
            type="password",
            help="Ingrese su API Key de Mistral para OCR",
        )
        if mistral_api_key and not mistral_api_key.startswith('your-'):
            os.environ["MISTRAL_API_KEY"] = mistral_api_key
            logging.info("Clave API de Mistral proporcionada por el usuario")

    # Obtener Assistant ID (primero de secrets.toml, luego de os.environ)
    assistant_id = None
    if hasattr(st, 'secrets') and 'ASSISTANT_ID' in st.secrets:
        assistant_id = st.secrets['ASSISTANT_ID']
        logging.info("ID de asistente cargado desde secrets.toml")
    else:
        assistant_id = os.environ.get("ASSISTANT_ID")
        logging.info("ID de asistente cargado desde variables de entorno")

    # Verificar configuración
    if openai_api_key and mistral_api_key:
        st.success(APP_IDENTITY["config_success"])
    else:
        missing = []
        if not openai_api_key:
            missing.append("API Key de OpenAI")
        if not mistral_api_key:
            missing.append("API Key de Mistral")
        st.warning(
            APP_IDENTITY["config_warning"].format(missing_items=", ".join(missing))
        )

    # Mostrar información del sistema
    st.info(f"Sistema inicializado correctamente")

    # Selector de expertos
    st.subheader("🤖 Expertos Disponibles")

    if "assistants_config" in st.session_state and st.session_state.assistants_config:
        # Crear opciones para el selector
        expert_options = {key: value["titulo"] for key, value in st.session_state.assistants_config.items()}

        # Obtener el índice del experto actual
        current_expert_key = st.session_state.current_expert
        current_expert_index = list(expert_options.keys()).index(current_expert_key) if current_expert_key in expert_options else 0

        # Selector de expertos
        selected_expert = st.selectbox(
            "Seleccionar experto:",
            options=list(expert_options.keys()),
            format_func=lambda x: expert_options[x],
            index=current_expert_index
        )

        # Opción para preservar el contexto
        preserve_context = st.checkbox("Preservar contexto y archivos", value=True, help="Mantiene los mensajes y archivos adjuntos al cambiar de experto")

        # Botón para confirmar el cambio de experto
        if st.button("Cambiar a este experto", use_container_width=True):
            if expert_selection.change_expert(selected_expert, "Cambio manual de experto", preserve_context):
                st.success(f"Experto cambiado a: {expert_options[selected_expert]}")
                st.rerun()
            else:
                st.error(f"No se pudo cambiar al experto seleccionado")
    else:
        st.warning("No se pudo cargar la configuración de expertos.")

    # Botón para reiniciar la conversación
    st.subheader("🔄 Reiniciar Conversación")
    if st.button("Nueva Conversación", use_container_width=True):
        # Crear un nuevo thread
        if "client" in st.session_state and st.session_state.client:
            thread = st.session_state.client.beta.threads.create()
            st.session_state.thread_id = thread.id
            # Limpiar mensajes y mantener el experto actual
            st.session_state.messages = []
            st.session_state.expert_history = []
            # Registrar el experto actual en el historial con formato de 12 horas
            st.session_state.expert_history.append({
                "timestamp": datetime.now().strftime("%I:%M:%S %p"),
                "expert": st.session_state.current_expert,
                "reason": "Nueva conversación"
            })
            st.success("Conversación reiniciada correctamente")
            st.rerun()

    # Historial de cambios de expertos
    if "expert_history" in st.session_state and len(st.session_state.expert_history) > 0:
        st.subheader("📜 Historial de Expertos")
        for entry in st.session_state.expert_history:
            expert_key = entry["expert"]
            if expert_key in st.session_state.assistants_config:
                expert_title = st.session_state.assistants_config[expert_key]["titulo"]
                st.markdown(f"""<div class='expert-history'>
                    <strong>{entry['timestamp']}</strong>: {expert_title}<br>
                    <small>{entry['reason']}</small>
                </div>""", unsafe_allow_html=True)

    # Opciones de exportación de chat
    st.subheader("💾 Exportar Conversación")
    export_format = st.radio("Formato de exportación:", ("Markdown", "PDF"))

    if st.button("Descargar conversación"):
        if "messages" in st.session_state and st.session_state.messages:
            if export_format == "Markdown":
                md_content = export_chat_to_markdown(st.session_state.messages)
                b64 = base64.b64encode(md_content.encode()).decode()
                href = f'<a href="data:text/markdown;base64,{b64}" download="{APP_IDENTITY["conversation_export_name"]}.md">Descargar archivo Markdown</a>'
                st.markdown(href, unsafe_allow_html=True)
            else:  # PDF
                try:
                    with st.spinner("Generando PDF..."):
                        try:
                            # Sistema de generación multicapa
                            content, content_type = export_chat_to_pdf(
                                st.session_state.messages
                            )
                            if content_type == "pdf":
                                b64 = base64.b64encode(content).decode()
                                href = f'<a href="data:application/pdf;base64,{b64}" download="{APP_IDENTITY["conversation_export_name"]}.pdf">Descargar archivo PDF</a>'
                                st.markdown(href, unsafe_allow_html=True)
                            else:
                                # Si devuelve markdown, mostrar alternativa
                                b64 = content  # Ya viene en base64
                                href = f'<a href="data:text/markdown;base64,{b64}" download="{APP_IDENTITY["conversation_export_name"]}.md">Descargar archivo Markdown</a>'
                                st.markdown(href, unsafe_allow_html=True)
                                st.warning(
                                    "No se pudo generar el PDF. Se ha creado un archivo markdown en su lugar."
                                )
                        except Exception as e:
                            st.error(f"Error durante la exportación: {str(e)}")
                            logging.error(f"Error detallado: {traceback.format_exc()}")
                except Exception as e:
                    st.error(f"Error al generar PDF: {str(e)}")
        else:
            st.warning("No hay conversación para exportar.")

    # Administrador de contexto de documentos
    st.subheader("📄 Gestión de Documentos")
    manage_document_context()

    # Verificación de documentos en contexto
    st.subheader("🔍 Verificación de Documentos")
    verify_document_context()

    # Botón para limpiar la sesión actual
    if st.button(
        "🧹 Limpiar sesión actual",
        type="secondary",
        help="Elimina todos los archivos y datos de la sesión actual",
    ):
        with st.spinner("Limpiando recursos de la sesión..."):
            result = clean_current_session()
            if isinstance(result, dict) and "error" not in result:
                st.success(
                    f"Sesión limpiada: {result['documents']} documentos, {result['messages']} mensajes"
                )
            else:
                st.error("No se pudo limpiar la sesión completamente")
            rerun_app()

    # Documentos cargados
    if "uploaded_files" in st.session_state and st.session_state.uploaded_files:
        st.subheader("📚 Documentos disponibles")
        for idx, filename in enumerate(st.session_state.uploaded_files):
            st.markdown(f"📄 **{filename}**")

        st.info("Estos documentos están disponibles para consulta en la conversación.")

    # Área informativa - Trasladada desde el cuerpo principal
    st.markdown("---")
    st.subheader(f"{APP_IDENTITY['icon']} Sobre {APP_IDENTITY['name']}")
    st.markdown(APP_IDENTITY["long_description"])

    # Añadir información de uso
    st.markdown("---")
    st.subheader("💡 Cómo usar " + APP_IDENTITY["name"])
    st.markdown(APP_IDENTITY["usage_instructions"])

    # Instrucciones para documentos
    st.markdown("---")
    st.subheader("📄 Procesamiento de documentos")
    st.info(APP_IDENTITY["document_processing_info"])
    st.caption(APP_IDENTITY["allowed_formats_message"])

    # Footer en la barra lateral
    st.markdown("---")
    st.subheader("Desarrollado por:")
    st.markdown(
        APP_IDENTITY["footer_text"].format(
            developer=APP_IDENTITY["developer"],
            github_url=APP_IDENTITY["github_url"],
            website_url=APP_IDENTITY["website_url"],
            linkedin_url=APP_IDENTITY["linkedin_url"],
            instagram_url=APP_IDENTITY["instagram_url"],
            twitter_url=APP_IDENTITY["twitter_url"],
            facebook_url=APP_IDENTITY["facebook_url"],
            whatsapp_url=APP_IDENTITY["whatsapp_url"],
            app_name=APP_IDENTITY["name"],
            app_version=APP_IDENTITY["version"],
            current_date=datetime.now().strftime("%Y-%m-%d"),
        ),
        unsafe_allow_html=True,
    )

# Detener si no tenemos la configuración completa
if not openai_api_key or not mistral_api_key or not assistant_id:
    st.markdown(f"⚠️ **Configuración incompleta**: Por favor, proporciona las claves API necesarias para {APP_IDENTITY['name']}")
    st.stop()



def change_expert(expert_key, reason="Selección manual", preserve_context=True):
    """
    Cambia el experto actual y registra el cambio en el historial.
    Esta función es un wrapper para la función del módulo expert_selection.

    Parámetros:
        expert_key: Clave del experto a seleccionar
        reason: Razón del cambio de experto
        preserve_context: Si se debe preservar el contexto (mensajes y archivos) entre cambios

    Retorno:
        bool: True si el cambio fue exitoso, False en caso contrario
    """
    # Usar la función del módulo expert_selection
    return expert_selection.change_expert(expert_key, reason, preserve_context)

# Diccionario de palabras clave para cada experto
keywords_dict = {
    "transformacion_digital": ["transformación digital", "tecnología", "innovación", "digital", "transformación"],
    "inteligencia_artificial": ["inteligencia artificial", "ia", "machine learning", "aprendizaje automático", "algoritmo", "modelo"],
    "asistente_virtual": ["asistente virtual", "chatbot", "bot", "automatización", "virtual"],
    "vigilancia_judicial": ["vigilancia judicial", "vigilancia", "seguimiento judicial", "monitoreo"],
    "constitucion": ["constitución", "constitucional", "derechos fundamentales", "carta política"],
    "proceso_civil": ["proceso civil", "código general del proceso", "cgp", "demanda", "contestación"],
    "derecho_disciplinario": ["derecho disciplinario", "disciplinario", "falta disciplinaria", "sanción"],
    "delitos_penales": ["delito", "penal", "código penal", "crimen", "pena"],
    "reclasificaciones": ["reclasificación", "clasificación", "categoría", "nivel"],
    "etica_educativa": ["ética educativa", "educación", "enseñanza", "pedagogía"],
    "resiliencia": ["resiliencia", "superación", "adversidad", "fortaleza"],
    "tributaria": ["tributario", "impuesto", "dian", "declaración", "renta"],
    "copywriting": ["copywriting", "redacción", "contenido", "texto", "escribir"],
    "asistente_personal": ["asistente personal", "agenda", "organización", "planificación"],
    "linguistica": ["lingüística", "gramática", "idioma", "lenguaje", "ortografía"],
    "analisis_documental": ["análisis documental", "documento", "revisión", "validación"],
    "justicia_lab": ["justicia lab", "innovación judicial", "laboratorio", "justicia"],
    "gestion_documental": ["gestión documental", "archivo", "documento", "expediente"],
    "salud_legal": ["salud", "médico", "paciente", "historia clínica", "eps"],
    "anticorrupcion": ["anticorrupción", "corrupción", "transparencia", "ética pública"],
    "calidad_salud": ["calidad en salud", "acreditación", "habilitación", "estándar"],
    "traslados_judiciales": ["traslado judicial", "traslado", "cambio de sede", "jurisdicción"],
    "evaluacion_judicial": ["evaluación judicial", "calificación", "desempeño", "funcionario"],
    "trading": ["trading", "inversión", "bolsa", "mercado", "acción", "finanzas"],
    "bochica": ["bochica", "vacante", "provisión", "cargo", "selección"],
    "tutela": ["tutela", "acción de tutela", "derecho de petición", "amparo", "protección"]
}

@handle_error(max_retries=1)
def detect_expert(message):
    """
    Analiza el texto del mensaje y sugiere el experto más adecuado.
    Esta función es un wrapper para la función del módulo expert_selection.

    Parámetros:
        message: Texto del mensaje del usuario

    Retorno:
        string: Clave del experto sugerido o None si no hay coincidencias
    """
    # Usar la función del módulo expert_selection
    return expert_selection.detect_expert(message, keywords_dict)



@handle_error(max_retries=1)
def process_message(message, expert_key):
    """
    Procesa un mensaje con el experto especificado.

    Parámetros:
        message: Texto del mensaje del usuario
        expert_key: Clave del experto a utilizar

    Retorno:
        string: Respuesta del asistente o None en caso de error
    """
    # Obtener el ID del asistente del expert_key
    assistant_id = st.session_state.assistants_config[expert_key]["id"]

    # Enriquecer el mensaje con el contenido de los documentos
    full_message = message

    # SIEMPRE verificar si hay documentos en la sesión
    if "document_contents" in st.session_state and st.session_state.document_contents:
        document_context = "\n\n### Contenido de documentos adjuntos:\n\n"

        # Filtrar archivos temporales
        temp_file_patterns = ["img-", "temp", "~$", ".tmp"]
        filtered_docs = {}
        for doc_name, doc_content in st.session_state.document_contents.items():
            # Verificar si parece un archivo temporal
            is_temp_file = any(pattern in doc_name.lower() for pattern in temp_file_patterns)
            if not is_temp_file:
                filtered_docs[doc_name] = doc_content

        # Usar los documentos filtrados
        for doc_name, doc_content in filtered_docs.items():
            # Extraer el texto del documento
            if isinstance(doc_content, dict) and "text" in doc_content:
                # Limitar el contenido para no exceder el contexto
                doc_text = doc_content["text"][:10000] + "..." if len(doc_content["text"]) > 10000 else doc_content["text"]
                document_context += f"-- Documento: {doc_name} --\n{doc_text}\n\n"
            elif isinstance(doc_content, dict) and "error" in doc_content:
                document_context += f"-- Documento: {doc_name} -- (Error: {doc_content.get('error', 'Error desconocido')})\n\n"

        # Añadir el contexto de documentos al mensaje si hay contenido real
        if len(document_context) > 60:  # Más que solo el encabezado
            full_message = f"{message}\n\n{document_context}"
            logging.info(f"Mensaje enriquecido con {len(filtered_docs)} documentos (filtrados de {len(st.session_state.document_contents)}). Tamaño total: {len(full_message)} caracteres")

    # Añadir el mensaje a la conversación
    st.session_state.client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=full_message
    )

    # Ejecutar el asistente con el thread actual
    run = st.session_state.client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=assistant_id
    )

    # Esperar a que el asistente termine de procesar
    with st.status("Procesando tu mensaje...", expanded=True) as status:
        run_counter = 0
        max_run_time = 120  # Tiempo máximo de espera (2 minutos)
        start_time = time.time()

        while run.status not in ["completed", "failed", "cancelled", "expired"]:
            run_counter += 1
            time.sleep(1)

            # Verificar timeout
            elapsed_time = time.time() - start_time
            if elapsed_time > max_run_time:
                status.update(
                    label="La operación está tomando demasiado tiempo. Intente nuevamente.",
                    state="error"
                )
                logging.error(f"Timeout después de {max_run_time}s esperando completar ejecución.")
                return None

            # Actualizar el estado cada 2 segundos para no sobrecargar la API
            if run_counter % 2 == 0:
                try:
                    run = st.session_state.client.beta.threads.runs.retrieve(
                        thread_id=st.session_state.thread_id, run_id=run.id
                    )
                    status.update(label=f"Procesando mensaje... ({run.status})")
                except Exception as e:
                    logging.warning(f"Error al recuperar estado de ejecución: {str(e)}")

    # Obtener los mensajes actualizados
    if run.status == "completed":
        messages = st.session_state.client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # Extraer la última respuesta del asistente
        for msg in messages.data:
            if msg.role == "assistant" and not any(m.get("id") == msg.id for m in st.session_state.messages):
                # Guardar el mensaje en el estado de la sesión
                new_message = {
                    "id": msg.id,
                    "role": "assistant",
                    "content": msg.content[0].text.value,
                    "expert": expert_key
                }
                st.session_state.messages.append(new_message)
                return new_message["content"]
    else:
        logging.error(f"La ejecución falló con estado: {run.status}")

        # Intentar usar modelo de respaldo si está configurado
        backup_model = os.environ.get("OPENAI_API_MODEL", "")
        if backup_model and "gpt-4.1-nano" in backup_model:
            try:
                logging.info(f"Intentando usar modelo de respaldo: {backup_model}")

                # Crear mensaje para el modelo de respaldo
                backup_messages = [
                    {"role": "system", "content": f"Eres un asistente virtual experto en {st.session_state.assistants_config[expert_key]['titulo']}. {st.session_state.assistants_config[expert_key]['descripcion']}"}
                ]

                # Añadir contexto de la conversación (hasta 5 mensajes previos)
                prev_messages = [m for m in st.session_state.messages if m.get("expert") == expert_key][-5:]
                for prev_msg in prev_messages:
                    backup_messages.append({"role": prev_msg["role"], "content": prev_msg["content"]})

                # Añadir el mensaje actual
                backup_messages.append({"role": "user", "content": full_message})

                # Llamar al modelo de respaldo
                backup_response = st.session_state.client.chat.completions.create(
                    model=backup_model,
                    messages=backup_messages,
                    temperature=0.7,
                    max_tokens=2000
                )

                if backup_response and backup_response.choices and len(backup_response.choices) > 0:
                    backup_text = backup_response.choices[0].message.content
                    logging.info(f"Respuesta obtenida del modelo de respaldo ({len(backup_text)} caracteres)")
                    return f"[Respuesta de respaldo usando {backup_model}]\n\n{backup_text}"
            except Exception as backup_error:
                logging.error(f"Error usando modelo de respaldo: {str(backup_error)}")

        return f"Lo siento, no pude procesar tu solicitud. Estado: {run.status}"

    return "Lo siento, no pude procesar tu solicitud en este momento."



# Crear clientes
openai_client = create_openai_client(openai_api_key)
st.session_state.client = openai_client

# Inicializar thread si no existe
if not st.session_state.thread_id and openai_client:
    with st.spinner("Inicializando sistema experto..."):
        thread_id = initialize_thread(openai_client)
        if thread_id:
            st.session_state.thread_id = thread_id
            st.success(
                f"{APP_IDENTITY['icon']} Sistema experto inicializado correctamente {APP_IDENTITY['icon']}"
            )

# ----- INTERFAZ DE CHAT -----

# Mostrar información del experto actual
if "current_expert" in st.session_state and st.session_state.current_expert in st.session_state.assistants_config:
    current_expert_key = st.session_state.current_expert
    current_expert = st.session_state.assistants_config[current_expert_key]

    st.markdown(f"""
    <div class="expert-card">
        <h3 style="margin-top: 0;">🤖 {current_expert["titulo"]}</h3>
        <p>{current_expert["descripcion"]}</p>
    </div>
    """, unsafe_allow_html=True)

# Contenedor de historial de chat - mostrar mensajes previos
chat_history_container = st.container()

with chat_history_container:
    # Mostrar mensajes previos
    for message in st.session_state.messages:
        # Si el mensaje es del asistente, mostrar el nombre del experto
        if message["role"] == "assistant" and "expert" in message:
            expert_key = message["expert"]
            if expert_key in st.session_state.assistants_config:
                expert_name = st.session_state.assistants_config[expert_key]["titulo"]
                with st.chat_message(message["role"]):
                    st.markdown(f"<div class='expert-name'>{expert_name}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='expert-message'>{message['content']}</div>", unsafe_allow_html=True)
        else:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Mostrar mensaje de bienvenida si no hay mensajes
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown(APP_IDENTITY["welcome_message"])

# Chat input con soporte nativo para adjuntar archivos
# Extraer extensiones sin el punto para el parámetro file_type
file_types = [ext[1:] for ext in ALLOWED_EXTENSIONS]  # Quitar el punto inicial

# Mostrar mensaje sobre formatos permitidos
st.caption(APP_IDENTITY["allowed_formats_message"])

# Input de chat con soporte para archivos
prompt = st.chat_input(
    APP_IDENTITY["chat_placeholder"],
    accept_file=True,
    file_type=file_types,
)

# Procesar la entrada del usuario
if prompt:
    # Verificar si hay texto o archivos
    user_text = ""
    user_files = []

    if hasattr(prompt, "text"):
        user_text = prompt.text

    if hasattr(prompt, "files") and prompt.files:
        user_files = prompt.files
    elif isinstance(prompt, dict) and "files" in prompt and prompt["files"]:
        user_files = prompt["files"]

    # Documentos para compartir en el contexto
    current_doc_contents = {}

    # Si hay archivos adjuntos, procesarlos con OCR
    if user_files:
        with st.spinner("Procesando documentos con OCR..."):
            valid_files = 0
            invalid_files = 0

            for file in user_files:
                # Validar el formato del archivo antes de procesarlo
                is_valid, file_type, error_message = validate_file_format(file)

                if not is_valid:
                    # Mostrar error y continuar con el siguiente archivo
                    st.error(f"Error en archivo {file.name}: {error_message}")
                    invalid_files += 1
                    continue

                # Si el archivo es válido, procesarlo
                if file.name not in st.session_state.uploaded_files:
                    st.session_state.uploaded_files.append(file.name)

                # Leer el contenido del archivo
                file_bytes = file.read()
                file.seek(0)  # Restaurar el puntero del archivo

                # Procesar con OCR de Mistral
                try:
                    # Registrar información detallada para depuración
                    logging.info(f"Iniciando procesamiento de {file.name} (tipo: {file_type}, tamaño: {len(file_bytes)} bytes)")

                    # Intentar extraer texto directamente para PDFs y Markdown antes de OCR
                    extracted_text = None
                    if file_type == "PDF":
                        try:
                            import PyPDF2
                            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                            pdf_text = ""
                            for page in pdf_reader.pages:
                                pdf_text += page.extract_text() + "\n\n"

                            if pdf_text.strip():
                                logging.info(f"Texto extraído directamente del PDF {file.name}: {len(pdf_text)} caracteres")
                                extracted_text = {"text": pdf_text, "format": "pdf_direct"}
                        except Exception as pdf_error:
                            logging.warning(f"Error extrayendo texto directo del PDF: {str(pdf_error)}")
                    elif file_type == "Markdown":
                        try:
                            # Procesar archivo Markdown
                            markdown_text = process_markdown_file(file_bytes)
                            if markdown_text and "text" in markdown_text:
                                logging.info(f"Texto extraído del archivo Markdown {file.name}: {len(markdown_text['text'])} caracteres")
                                extracted_text = markdown_text
                        except Exception as md_error:
                            logging.warning(f"Error procesando archivo Markdown: {str(md_error)}")

                    # Si no pudimos extraer texto directamente, usar OCR
                    if not extracted_text:
                        ocr_results = process_document_with_mistral_ocr(
                            mistral_api_key, file_bytes, file_type, file.name
                        )

                        if ocr_results and "error" not in ocr_results:
                            extracted_text = ocr_results
                        else:
                            error_msg = ocr_results.get("error", "Error desconocido durante el procesamiento")
                            logging.error(f"Error en OCR para {file.name}: {error_msg}")
                            # Intentar guardar el contenido crudo como respaldo
                            if "raw_response" in ocr_results:
                                extracted_text = {"text": f"Error en OCR: {error_msg}\n\nRespuesta cruda: {str(ocr_results['raw_response'])[:1000]}", "format": "error_with_raw"}
                            else:
                                extracted_text = {"text": f"Error en OCR: {error_msg}", "format": "error"}

                    # Guardar el resultado final
                    if extracted_text:
                        current_doc_contents[file.name] = extracted_text
                        # Guardar en la sesión para referencia futura
                        st.session_state.document_contents[file.name] = extracted_text
                        st.success(f"Documento {file.name} procesado correctamente")
                        logging.info(f"Documento {file.name} procesado exitosamente con formato {extracted_text.get('format', 'desconocido')}")
                        valid_files += 1
                    else:
                        st.warning(f"No se pudo extraer texto de {file.name}")
                        logging.warning(f"No se pudo extraer texto de {file.name}")
                except Exception as e:
                    st.error(f"Error procesando {file.name}: {str(e)}")
                    logging.error(f"Excepción procesando {file.name}: {str(e)}")
                    logging.error(traceback.format_exc())

            # Mostrar resumen de procesamiento
            if invalid_files > 0:
                st.warning(
                    f"{invalid_files} archivo(s) no válido(s) fueron omitidos. {APP_IDENTITY['allowed_formats_message']}"
                )

                # Si todos los archivos fueron inválidos, mostrar mensaje más claro
                if invalid_files == len(user_files) and len(user_files) > 0:
                    st.error(
                        "No se pudo procesar ningún archivo. Verifique que los archivos cumplan con los formatos permitidos y no estén corruptos."
                    )

    # Generar un mensaje automático si solo hay archivos sin texto
    if not user_text and user_files:
        file_names = [f.name for f in user_files]

        # Verificar si hay contenido de archivos para incluirlo en el mensaje
        file_contents = ""
        for file_name, content in current_doc_contents.items():
            # Procesar archivos de texto
            if file_name.lower().endswith('.txt') and 'text' in content:
                file_contents += f"\n\nContenido de {file_name}:\n```\n{content['text'][:5000]}\n```"
                if len(content['text']) > 5000:
                    file_contents += "\n[Contenido truncado por longitud...]\n"
            # Procesar archivos PDF
            elif (file_name.lower().endswith('.pdf') and 'text' in content):
                file_contents += f"\n\nContenido del PDF {file_name}:\n```\n{content['text'][:5000]}\n```"
                if len(content['text']) > 5000:
                    file_contents += "\n[Contenido truncado por longitud...]\n"
            # Procesar archivos Markdown
            elif (file_name.lower().endswith('.md') and 'text' in content):
                file_contents += f"\n\nContenido del Markdown {file_name}:\n```markdown\n{content['text'][:5000]}\n```"
                if len(content['text']) > 5000:
                    file_contents += "\n[Contenido truncado por longitud...]\n"
            # Procesar otros tipos de archivos con texto
            elif 'text' in content and content['text']:
                file_contents += f"\n\nContenido de {file_name}:\n```\n{content['text'][:5000]}\n```"
                if len(content['text']) > 5000:
                    file_contents += "\n[Contenido truncado por longitud...]\n"

        # Mensaje base
        user_text = APP_IDENTITY["file_upload_default_message"].format(
            files=", ".join(file_names)
        )

        # Añadir contenido de archivos si existe
        if file_contents:
            user_text += file_contents
            logging.info(f"Mensaje generado con contenido de {len(current_doc_contents)} archivos")

    # Si no hay ni texto ni archivos, no hacemos nada
    if not user_text and not user_files:
        st.warning("Por favor, ingrese un mensaje o adjunte un archivo para continuar.")
    else:
        # Construir el mensaje para mostrar
        display_message = user_text
        if user_files:
            file_names = [f.name for f in user_files]
            if user_text:
                display_message = (
                    f"{user_text}\n\n*Archivo adjunto: {', '.join(file_names)}*"
                )
            else:
                display_message = (
                    f"*Archivo adjunto para análisis: {', '.join(file_names)}*"
                )

        # Mostrar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": display_message})
        with st.chat_message("user"):
            st.markdown(display_message)

        # Procesar la respuesta usando el contenido de los documentos
        if st.session_state.thread_id and "client" in st.session_state and st.session_state.client:
            try:

                # Si llegamos aquí, continuamos con el flujo normal (procesar con el experto actual)
                with st.spinner(f"Procesando tu mensaje con {st.session_state.assistants_config[st.session_state.current_expert]['titulo']}..."):
                    response_text = process_message(user_text, st.session_state.current_expert)
                    if response_text:
                        st.rerun()
                    else:
                        st.error(APP_IDENTITY["response_error"])
            except Exception as e:
                st.error(f"Error: {str(e)}")
                logging.error(f"Error en procesamiento de mensaje: {str(e)}")
                logging.error(traceback.format_exc())
        else:
            st.error("No se pudo conectar con el asistente. Verifique la configuración.")
