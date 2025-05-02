"""
Script de prueba para validar el procesamiento de documentos y mantenimiento del contexto
en Expert Nexus.

Este script simula el flujo de carga de documentos y conversación con el asistente,
verificando que los documentos se mantienen correctamente en el contexto.
"""

import os
import sys
import io
import json
import logging
import base64
from datetime import datetime
from openai import OpenAI

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - TEST - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Directorio actual y directorio raíz del proyecto
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))

# Añadir el directorio raíz al path para importar módulos del proyecto
sys.path.append(root_dir)

# Importar funciones necesarias del proyecto
try:
    from app import process_document_with_mistral_ocr, validate_file_format
    logging.info("Módulos importados correctamente")
except ImportError as e:
    logging.error(f"Error importando módulos: {str(e)}")
    sys.exit(1)

# Configuración de prueba
TEST_CONFIG = {
    "openai_api_key": os.environ.get("OPENAI_API_KEY"),
    "mistral_api_key": os.environ.get("MISTRAL_API_KEY"),
    "assistant_id": os.environ.get("ASSISTANT_ID"),
    "test_files_dir": os.path.join(current_dir, "test_files"),
}

# Verificar configuración
if not TEST_CONFIG["openai_api_key"]:
    logging.error("OPENAI_API_KEY no está configurada")
    sys.exit(1)
if not TEST_CONFIG["mistral_api_key"]:
    logging.error("MISTRAL_API_KEY no está configurada")
    sys.exit(1)
if not TEST_CONFIG["assistant_id"]:
    logging.error("ASSISTANT_ID no está configurada")
    sys.exit(1)

# Crear directorio de archivos de prueba si no existe
os.makedirs(TEST_CONFIG["test_files_dir"], exist_ok=True)

# Clase para simular un archivo cargado por Streamlit
class MockFile:
    def __init__(self, path, content=None):
        self.name = os.path.basename(path)
        self._content = content if content else open(path, "rb").read()
        self._position = 0

    def read(self):
        self._position = len(self._content)
        return self._content

    def tell(self):
        return self._position

    def seek(self, position):
        self._position = position

# Función para crear un cliente OpenAI
def create_openai_client(api_key):
    try:
        client = OpenAI(
            api_key=api_key,
            default_headers={"OpenAI-Beta": "assistants=v2"}
        )
        # Verificar conectividad
        models = client.models.list()
        if models:
            logging.info(f"Cliente OpenAI inicializado correctamente. Modelos disponibles: {len(models.data)}")
            return client
        else:
            logging.error("No se pudo obtener la lista de modelos")
            return None
    except Exception as e:
        logging.error(f"Error inicializando cliente OpenAI: {str(e)}")
        return None

# Función para inicializar un thread
def initialize_thread(client):
    try:
        thread = client.beta.threads.create()
        thread_id = thread.id
        logging.info(f"Thread creado: {thread_id}")
        return thread_id
    except Exception as e:
        logging.error(f"Error creando thread: {str(e)}")
        return None

# Función para procesar un documento
def process_document(file_path, mistral_api_key):
    try:
        # Crear un archivo simulado
        mock_file = MockFile(file_path)

        # Validar formato
        is_valid, file_type, error_message = validate_file_format(mock_file)

        if not is_valid:
            logging.error(f"Formato de archivo no válido: {error_message}")
            return None

        # Leer contenido
        mock_file.seek(0)
        file_bytes = mock_file.read()

        # Procesar documento
        logging.info(f"Procesando documento {mock_file.name} (tipo: {file_type})")
        result = process_document_with_mistral_ocr(
            mistral_api_key, file_bytes, file_type, mock_file.name
        )

        if result and "error" not in result:
            logging.info(f"Documento procesado correctamente: {len(result.get('text', ''))} caracteres")
            return result
        else:
            error_msg = result.get("error", "Error desconocido")
            logging.error(f"Error procesando documento: {error_msg}")
            return None
    except Exception as e:
        logging.error(f"Error en process_document: {str(e)}")
        return None

# Función para enviar mensaje con contexto de documentos
def send_message_with_context(client, thread_id, assistant_id, message, document_contents):
    try:
        # Construir mensaje con contexto de documentos
        full_message = message

        if document_contents:
            document_context = "\n\n### Contenido de documentos adjuntos:\n\n"

            for doc_name, doc_content in document_contents.items():
                if isinstance(doc_content, dict) and "text" in doc_content:
                    # Limitar contenido para no exceder el contexto
                    doc_text = doc_content["text"][:10000] + "..." if len(doc_content["text"]) > 10000 else doc_content["text"]
                    document_context += f"-- Documento: {doc_name} --\n{doc_text}\n\n"

            # Añadir contexto al mensaje
            full_message = f"{message}\n\n{document_context}"
            logging.info(f"Mensaje enriquecido con {len(document_contents)} documentos. Tamaño total: {len(full_message)} caracteres")

        # Enviar mensaje
        message_obj = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=full_message
        )
        logging.info(f"Mensaje enviado: {message_obj.id}")

        # Ejecutar asistente
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        logging.info(f"Ejecución iniciada: {run.id}")

        # Esperar a que termine
        while run.status not in ["completed", "failed", "cancelled", "expired"]:
            logging.info(f"Estado de ejecución: {run.status}")
            import time
            time.sleep(2)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )

        logging.info(f"Ejecución finalizada: {run.status}")

        # Obtener respuesta
        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread_id)

            # Buscar el mensaje más reciente del asistente
            for msg in messages.data:
                if msg.role == "assistant":
                    response_content = ""
                    for content_item in msg.content:
                        if hasattr(content_item, "text") and content_item.text:
                            response_content += content_item.text.value

                    logging.info(f"Respuesta recibida ({len(response_content)} caracteres)")
                    return response_content

            logging.warning("No se encontró respuesta del asistente")
            return None
        else:
            logging.error(f"La ejecución falló: {run.status}")
            return None
    except Exception as e:
        logging.error(f"Error en send_message_with_context: {str(e)}")
        return None

# Función para crear un archivo PDF de prueba
def create_test_pdf():
    try:
        from fpdf import FPDF

        pdf_path = os.path.join(TEST_CONFIG["test_files_dir"], "test_document.pdf")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", size=12)

        # Título
        pdf.set_font("helvetica", style="B", size=16)
        pdf.cell(200, 10, "Documento de Prueba para Expert Nexus", ln=True, align="C")
        pdf.ln(10)

        # Contenido
        pdf.set_font("helvetica", size=12)
        pdf.multi_cell(0, 10, "Este es un documento PDF de prueba para verificar el procesamiento de documentos en Expert Nexus.")
        pdf.ln(5)

        pdf.multi_cell(0, 10, "El sistema debe ser capaz de extraer este texto y mantenerlo en el contexto de la conversación.")
        pdf.ln(5)

        pdf.multi_cell(0, 10, "Información clave para verificar: Expert Nexus versión 1.0.0, fecha de prueba: " + datetime.now().strftime("%Y-%m-%d"))

        # Guardar PDF
        pdf.output(pdf_path)
        logging.info(f"Archivo PDF de prueba creado: {pdf_path}")
        return pdf_path
    except Exception as e:
        logging.error(f"Error creando PDF de prueba: {str(e)}")
        return None

# Función para crear un archivo de texto de prueba
def create_test_text():
    try:
        text_path = os.path.join(TEST_CONFIG["test_files_dir"], "test_document.txt")

        with open(text_path, "w") as f:
            f.write("Documento de texto de prueba para Expert Nexus\n\n")
            f.write("Este archivo contiene información que debe ser procesada y mantenida en el contexto.\n\n")
            f.write("Datos de prueba: código secreto 12345, fecha: " + datetime.now().strftime("%Y-%m-%d"))

        logging.info(f"Archivo de texto de prueba creado: {text_path}")
        return text_path
    except Exception as e:
        logging.error(f"Error creando archivo de texto de prueba: {str(e)}")
        return None

# Función principal de prueba
def run_test():
    results = {
        "success": False,
        "document_processing": {},
        "conversation": [],
        "errors": []
    }

    try:
        # Crear cliente OpenAI
        client = create_openai_client(TEST_CONFIG["openai_api_key"])
        if not client:
            results["errors"].append("No se pudo crear el cliente OpenAI")
            return results

        # Inicializar thread
        thread_id = initialize_thread(client)
        if not thread_id:
            results["errors"].append("No se pudo inicializar el thread")
            return results

        # Crear archivos de prueba
        pdf_path = create_test_pdf()
        text_path = create_test_text()

        if not pdf_path or not text_path:
            results["errors"].append("No se pudieron crear los archivos de prueba")
            return results

        # Procesar documentos
        document_contents = {}

        # Procesar PDF
        pdf_result = process_document(pdf_path, TEST_CONFIG["mistral_api_key"])
        if pdf_result:
            document_contents[os.path.basename(pdf_path)] = pdf_result
            results["document_processing"]["pdf"] = {
                "success": True,
                "text_length": len(pdf_result.get("text", "")),
                "format": pdf_result.get("format", "unknown")
            }
        else:
            results["document_processing"]["pdf"] = {"success": False}
            results["errors"].append("Error procesando PDF")

        # Procesar texto
        text_result = process_document(text_path, TEST_CONFIG["mistral_api_key"])
        if text_result:
            document_contents[os.path.basename(text_path)] = text_result
            results["document_processing"]["text"] = {
                "success": True,
                "text_length": len(text_result.get("text", "")),
                "format": text_result.get("format", "unknown")
            }
        else:
            results["document_processing"]["text"] = {"success": False}
            results["errors"].append("Error procesando archivo de texto")

        # Prueba 1: Preguntar sobre los documentos
        message1 = "¿Qué documentos tengo cargados y qué información contienen?"
        response1 = send_message_with_context(
            client, thread_id, TEST_CONFIG["assistant_id"],
            message1, document_contents
        )

        results["conversation"].append({
            "user": message1,
            "assistant": response1,
            "documents_in_context": list(document_contents.keys())
        })

        # Prueba 2: Preguntar sobre información específica
        message2 = "¿Cuál es el código secreto mencionado en el documento de texto?"
        response2 = send_message_with_context(
            client, thread_id, TEST_CONFIG["assistant_id"],
            message2, document_contents
        )

        results["conversation"].append({
            "user": message2,
            "assistant": response2,
            "documents_in_context": list(document_contents.keys())
        })

        # Prueba 3: Preguntar sin mencionar documentos para ver si mantiene el contexto
        message3 = "¿Cuál es la fecha mencionada en los documentos?"
        response3 = send_message_with_context(
            client, thread_id, TEST_CONFIG["assistant_id"],
            message3, document_contents
        )

        results["conversation"].append({
            "user": message3,
            "assistant": response3,
            "documents_in_context": list(document_contents.keys())
        })

        # Prueba 4: Preguntar sin incluir documentos para verificar si se pierde el contexto
        message4 = "¿Sigues teniendo acceso a la información de los documentos?"
        response4 = send_message_with_context(
            client, thread_id, TEST_CONFIG["assistant_id"],
            message4, {}  # Sin documentos
        )

        results["conversation"].append({
            "user": message4,
            "assistant": response4,
            "documents_in_context": []
        })

        # Prueba 5: Volver a incluir documentos para ver si recupera el contexto
        message5 = "Ahora que te he vuelto a proporcionar los documentos, ¿puedes decirme qué versión de Expert Nexus se menciona en el PDF?"
        response5 = send_message_with_context(
            client, thread_id, TEST_CONFIG["assistant_id"],
            message5, document_contents
        )

        results["conversation"].append({
            "user": message5,
            "assistant": response5,
            "documents_in_context": list(document_contents.keys())
        })

        results["success"] = True
        return results
    except Exception as e:
        logging.error(f"Error en run_test: {str(e)}")
        results["errors"].append(f"Error general: {str(e)}")
        return results

# Ejecutar prueba y guardar resultados
if __name__ == "__main__":
    logging.info("Iniciando prueba de procesamiento de documentos y contexto")

    # Ejecutar prueba
    test_results = run_test()

    # Guardar resultados
    results_path = os.path.join(TEST_CONFIG["test_files_dir"], "test_results.json")
    with open(results_path, "w") as f:
        json.dump(test_results, f, indent=2)

    logging.info(f"Resultados guardados en: {results_path}")

    # Mostrar resumen
    if test_results["success"]:
        logging.info("Prueba completada con éxito")
    else:
        logging.error(f"Prueba fallida. Errores: {test_results['errors']}")

    # Mostrar resultados de procesamiento de documentos
    for doc_type, result in test_results["document_processing"].items():
        if result["success"]:
            logging.info(f"Documento {doc_type} procesado correctamente: {result['text_length']} caracteres")
        else:
            logging.error(f"Error procesando documento {doc_type}")

    # Mostrar resultados de conversación
    for i, exchange in enumerate(test_results["conversation"]):
        logging.info(f"Intercambio {i+1}:")
        logging.info(f"  Usuario: {exchange['user']}")
        logging.info(f"  Asistente: {exchange['assistant'][:100]}..." if exchange['assistant'] and len(exchange['assistant']) > 100 else f"  Asistente: {exchange['assistant']}")
        logging.info(f"  Documentos en contexto: {exchange['documents_in_context']}")
