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
    "icon": "🧠🔄",
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

    **Formatos soportados**: PDF (.pdf), Texto (.txt), Imágenes (.jpg, .jpeg, .png). Otros formatos no serán procesados.
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
    "allowed_formats_message": "Formatos permitidos: PDF (.pdf), Texto (.txt), Imágenes (.jpg, .jpeg, .png)",
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

# Inicializar variables con valores predeterminados
os.environ["OPENAI_API_KEY"] = assistants_config.OPENAI_API_KEY
os.environ["MISTRAL_API_KEY"] = assistants_config.MISTRAL_API_KEY
os.environ["ASSISTANT_ID"] = assistants_config.ASSISTANT_ID

# Sobrescribir con secrets si están disponibles
if hasattr(st, 'secrets'):
    try:
        # Cargar clave API de OpenAI
        if 'openai' in st.secrets and 'api_key' in st.secrets['openai']:
            openai_key = st.secrets["openai"]["api_key"]
            if openai_key and not openai_key.startswith('sk-your-'):
                os.environ["OPENAI_API_KEY"] = openai_key
                logging.info("Clave API de OpenAI cargada desde secrets")

        # Cargar clave API de Mistral
        if 'mistral' in st.secrets and 'api_key' in st.secrets['mistral']:
            os.environ["MISTRAL_API_KEY"] = st.secrets["mistral"]["api_key"]
            logging.info("Clave API de Mistral cargada desde secrets")

        # Cargar ID del asistente
        if 'openai' in st.secrets and 'assistant_id' in st.secrets['openai']:
            os.environ["ASSISTANT_ID"] = st.secrets["openai"]["assistant_id"]
            logging.info("ID del asistente cargado desde secrets")

    except Exception as e:
        logging.error(f"Error al cargar secrets: {str(e)}")
        # Ya tenemos los valores predeterminados, no es necesario hacer nada más

# Verificar que las claves no sean placeholders
if os.environ["OPENAI_API_KEY"].startswith('sk-your-'):
    logging.error("La clave API de OpenAI parece ser un placeholder")
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
    /* Estilos para la tarjeta de experto */
    .expert-card {
        padding: 15px;
        border-radius: 8px;
        background-color: #f0f2f6;
        margin-bottom: 20px;
        border-left: 4px solid #1E88E5;
    }

    /* Estilos para el historial de expertos */
    .expert-history {
        border-left: 2px solid #1E88E5;
        padding-left: 10px;
        margin-bottom: 8px;
    }

    /* Estilos para los mensajes de chat */
    .expert-message {
        background-color: #f0f7ff;
        padding: 5px 0;
        border-radius: 4px;
    }

    /* Estilos para los botones de selección de experto */
    .stButton button {
        width: 100%;
        border-radius: 20px;
    }

    /* Estilos para el nombre del experto en los mensajes */
    .expert-name {
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 5px;
    }
</style>
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
            error_msg = f"Clave API inválida: {api_key[:10]}..."
            logging.error(error_msg)
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
def export_chat_to_pdf(messages):
    """
    Sistema multicapa para exportación de conversaciones a PDF.
    Implementa múltiples estrategias de generación con manejo de fallos.
    """
    try:
        # Método 1 (preferido): FPDF con manejo mejorado
        return _export_chat_to_pdf_primary(messages)
    except Exception as e:
        logging.warning(f"Método primario de exportación a PDF falló: {str(e)}")
        try:
            # Método 2: ReportLab como alternativa
            return _export_chat_to_pdf_secondary(messages)
        except Exception as e2:
            logging.warning(f"Método secundario de exportación a PDF falló: {str(e2)}")
            try:
                # Método 3: Conversión simple como último recurso
                return _export_chat_to_pdf_fallback(messages)
            except Exception as e3:
                logging.error(
                    f"Todos los métodos de exportación a PDF fallaron: {str(e3)}"
                )
                # Último recurso: Devolver contenido en markdown codificado
                md_content = export_chat_to_markdown(messages)
                st.warning(
                    "No fue posible generar un PDF. Se ha creado un archivo markdown en su lugar."
                )
                return base64.b64encode(md_content.encode()).decode(), "markdown"


def _export_chat_to_pdf_primary(messages):
    """
    Método primario: FPDF optimizado con manejo de errores mejorado
    y división inteligente de texto para evitar problemas de espacio
    """
    from fpdf import FPDF
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
    con manejo mejorado de texto extenso
    """
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
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
    con mejoras de formato y legibilidad
    """
    md_content = f"# {APP_IDENTITY['name']} - Historial de Conversación\n\n"
    md_content += f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    for msg in messages:
        role = "Usuario" if msg["role"] == "user" else APP_IDENTITY["name"]
        md_content += f"## {role}\n\n{msg['content']}\n\n"
        md_content += "---\n\n"  # Separador para mejorar legibilidad

    return md_content


# Definición de formatos permitidos y sus extensiones
ALLOWED_FILE_FORMATS = {
    "PDF": [".pdf"],
    "Imagen": [".jpg", ".jpeg", ".png"],
    "Texto": [".txt"],
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

    # 2. Verificar por extensión del nombre
    if hasattr(file, "name"):
        name = file.name.lower()
        if name.endswith(".pdf"):
            return "PDF"
        elif name.endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp")):
            return "Imagen"

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
    Carga la configuración de asistentes desde la configuración predefinida
    """
    try:
        # Usar directamente la configuración predefinida para evitar problemas de serialización
        logging.info("Usando configuración predefinida de asistentes")
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
    # Establecer un experto predeterminado (asistente_virtual)
    default_expert = "asistente_virtual"
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

    # Obtener API Key de OpenAI
    openai_api_key = None
    # 1. Intentar obtener de variables de entorno
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    # 2. Intentar obtener de secrets.toml
    if not openai_api_key and hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
        openai_api_key = st.secrets["OPENAI_API_KEY"]

    # 3. Solicitar al usuario
    if not openai_api_key:
        openai_api_key = st.text_input(
            "API Key de OpenAI", type="password", help="Ingrese su API Key de OpenAI"
        )

    # Obtener API Key de Mistral
    mistral_api_key = None
    # 1. Intentar obtener de variables de entorno
    mistral_api_key = os.environ.get("MISTRAL_API_KEY")

    # 2. Intentar obtener de secrets.toml
    if (
        not mistral_api_key
        and hasattr(st, "secrets")
        and "MISTRAL_API_KEY" in st.secrets
    ):
        mistral_api_key = st.secrets["MISTRAL_API_KEY"]

    # 3. Solicitar al usuario
    if not mistral_api_key:
        mistral_api_key = st.text_input(
            "API Key de Mistral",
            type="password",
            help="Ingrese su API Key de Mistral para OCR",
        )

    # Obtener Assistant ID - Ya no se usa directamente, se usa el ID del experto actual
    assistant_id = None
    # 1. Intentar obtener de variables de entorno
    assistant_id = os.environ.get("ASSISTANT_ID")

    # 2. Intentar obtener de secrets.toml
    if not assistant_id and hasattr(st, "secrets") and "ASSISTANT_ID" in st.secrets:
        assistant_id = st.secrets["ASSISTANT_ID"]

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
    # export_format = st.radio("Formato de exportación:", ("Markdown", "PDF"))
    export_format = st.radio("Formato de exportación:", ("Markdown"))

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

    # Añadir el mensaje a la conversación
    st.session_state.client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=message
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

                    # Intentar extraer texto directamente para PDFs antes de OCR
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
