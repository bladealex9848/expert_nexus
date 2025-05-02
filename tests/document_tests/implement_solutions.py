"""
Script para implementar las soluciones propuestas a los problemas de procesamiento
de documentos en Expert Nexus.
"""

import os
import sys
import re
import logging
import shutil
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - IMPLEMENT - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Directorio actual y directorio raíz del proyecto
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))

# Función para hacer backup del archivo app.py
def backup_app_file():
    app_path = os.path.join(root_dir, "app.py")
    if not os.path.exists(app_path):
        logging.error(f"No se encontró el archivo app.py en {root_dir}")
        return False

    # Crear directorio de backup si no existe
    backup_dir = os.path.join(current_dir, "backups")
    os.makedirs(backup_dir, exist_ok=True)

    # Crear nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"app_{timestamp}.py.bak")

    # Copiar archivo
    try:
        shutil.copy2(app_path, backup_path)
        logging.info(f"Backup creado: {backup_path}")
        return True
    except Exception as e:
        logging.error(f"Error creando backup: {str(e)}")
        return False

# Función para modificar la función process_message
def modify_process_message():
    app_path = os.path.join(root_dir, "app.py")

    try:
        # Leer el archivo
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Buscar la función process_message
        process_message_pattern = r'@handle_error\(max_retries=1\)\s*def process_message\(message, expert_key\):.*?# Añadir el mensaje a la conversación.*?content=([^)]+)\s*\)'

        # Usar re.DOTALL para que el punto coincida con saltos de línea
        match = re.search(process_message_pattern, content, re.DOTALL)

        if not match:
            logging.error("No se pudo encontrar la función process_message en app.py")
            return False

        # Obtener el contenido actual de la función
        current_function = match.group(0)

        # Verificar si ya está modificada
        if "# SIEMPRE verificar si hay documentos en la sesión" in current_function:
            logging.info("La función process_message ya está modificada")
            return True

        # Crear la nueva versión de la función
        new_function = """@handle_error(max_retries=1)
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
        document_context = "\\n\\n### Contenido de documentos adjuntos:\\n\\n"

        for doc_name, doc_content in st.session_state.document_contents.items():
            # Extraer el texto del documento
            if isinstance(doc_content, dict) and "text" in doc_content:
                # Limitar el contenido para no exceder el contexto
                doc_text = doc_content["text"][:10000] + "..." if len(doc_content["text"]) > 10000 else doc_content["text"]
                document_context += f"-- Documento: {doc_name} --\\n{doc_text}\\n\\n"
            elif isinstance(doc_content, dict) and "error" in doc_content:
                document_context += f"-- Documento: {doc_name} -- (Error: {doc_content.get('error', 'Error desconocido')})\\n\\n"

        # Añadir el contexto de documentos al mensaje si hay contenido real
        if len(document_context) > 60:  # Más que solo el encabezado
            full_message = f"{message}\\n\\n{document_context}"
            logging.info(f"Mensaje enriquecido con {len(st.session_state.document_contents)} documentos. Tamaño total: {len(full_message)} caracteres")

    # Añadir el mensaje a la conversación
    st.session_state.client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=full_message
    )"""

        # Reemplazar la función en el contenido
        new_content = content.replace(current_function, new_function)

        # Guardar el archivo modificado
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        logging.info("Función process_message modificada correctamente")
        return True

    except Exception as e:
        logging.error(f"Error modificando process_message: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return False

# Función para añadir un sistema de verificación de documentos
def add_document_verification():
    app_path = os.path.join(root_dir, "app.py")

    try:
        # Leer el archivo
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verificar si ya existe la función
        if "def verify_document_context():" in content:
            logging.info("La función verify_document_context ya existe")
            return True

        # Buscar un buen lugar para añadir la función (después de manage_document_context)
        manage_doc_pattern = r'def manage_document_context\(\):.*?st\.info\("No hay documentos cargados en el contexto actual\."\)'

        # Usar re.DOTALL para que el punto coincida con saltos de línea
        match = re.search(manage_doc_pattern, content, re.DOTALL)

        if not match:
            logging.error("No se pudo encontrar un lugar adecuado para añadir la función")
            return False

        # Obtener la posición donde termina la función manage_document_context
        end_pos = match.end()

        # Crear la nueva función
        new_function = """


# Función para verificar el contexto de documentos
@handle_error(max_retries=0)
def verify_document_context():
    """
    Verifica que los documentos en el contexto estén correctamente procesados
    y disponibles para el asistente.
    """
    if "document_contents" in st.session_state and st.session_state.document_contents:
        st.write("### Verificación de documentos en contexto")

        # Verificar cada documento
        for doc_name, doc_content in st.session_state.document_contents.items():
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

        # Botón para refrescar documentos
        if st.button("Refrescar documentos en contexto"):
            st.success("Contexto de documentos actualizado")
            # Usar sistema seguro de reinicio
            rerun_app()
    else:
        st.info("No hay documentos en el contexto actual.")"""

        # Insertar la nueva función después de manage_document_context
        new_content = content[:end_pos] + new_function + content[end_pos:]

        # Guardar el archivo modificado
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        logging.info("Función verify_document_context añadida correctamente")

        # Ahora, añadir la llamada a la función en la barra lateral
        sidebar_pattern = r'# Administrador de contexto de documentos\s*st\.subheader\("📄 Gestión de Documentos"\)\s*manage_document_context\(\)'

        match = re.search(sidebar_pattern, new_content)

        if not match:
            logging.warning("No se pudo encontrar el lugar para añadir la llamada a verify_document_context")
            return True

        # Obtener la posición donde termina la llamada a manage_document_context
        end_pos = match.end()

        # Añadir la llamada a verify_document_context
        sidebar_addition = "\n\n    # Verificación de documentos en contexto\n    st.subheader(\"🔍 Verificación de Documentos\")\n    verify_document_context()"

        # Insertar la llamada
        final_content = new_content[:end_pos] + sidebar_addition + new_content[end_pos:]

        # Guardar el archivo modificado
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(final_content)

        logging.info("Llamada a verify_document_context añadida a la barra lateral")
        return True

    except Exception as e:
        logging.error(f"Error añadiendo verify_document_context: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return False

# Función principal
def main():
    logging.info("Implementando soluciones para Expert Nexus...")

    # Hacer backup del archivo app.py
    if not backup_app_file():
        logging.error("No se pudo crear backup. Abortando implementación.")
        return

    # Modificar la función process_message
    if not modify_process_message():
        logging.error("No se pudo modificar la función process_message. Abortando implementación.")
        return

    # Añadir sistema de verificación de documentos
    if not add_document_verification():
        logging.warning("No se pudo añadir el sistema de verificación de documentos.")

    logging.info("Implementación completada con éxito.")
    logging.info("Se recomienda ejecutar las pruebas nuevamente para verificar las mejoras.")

if __name__ == "__main__":
    main()
