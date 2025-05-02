#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba específico para el método de conversión optimizado para Streamlit Cloud.
Este script prueba la conversión de Markdown a PDF utilizando pdfkit y markdown2.
"""

import os
import sys
import logging
import tempfile
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('streamlit_cloud_test')

# Añadir el directorio raíz al path para importar módulos de la aplicación
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, root_dir)
print(f"Directorio raíz: {root_dir}")

# Verificar dependencias necesarias
try:
    import pdfkit
    import markdown2
    import pygments
    logger.info("Todas las dependencias necesarias están instaladas")
except ImportError as e:
    logger.error(f"Falta una dependencia necesaria: {e}")
    logger.error("Por favor, instala las dependencias con: pip install pdfkit markdown2 pygments")
    sys.exit(1)

# Importar la función de conversión específica
try:
    from app import _export_chat_to_pdf_streamlit_cloud
except ImportError as e:
    logger.error(f"Error al importar la función de conversión: {e}")
    sys.exit(1)

def read_markdown_file(file_path):
    """Lee un archivo Markdown y devuelve su contenido."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error al leer el archivo {file_path}: {e}")
        return None

def save_pdf_file(pdf_content, output_path):
    """Guarda el contenido PDF en un archivo."""
    try:
        with open(output_path, 'wb') as f:
            f.write(pdf_content)
        logger.info(f"PDF guardado en: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error al guardar el PDF en {output_path}: {e}")
        return False

def format_markdown_as_messages(markdown_content):
    """
    Convierte el contenido Markdown en un formato de mensajes
    similar al utilizado en la aplicación.
    """
    # Crear un mensaje simple para las pruebas
    messages = [
        {
            "role": "system",
            "content": "Conversión de prueba de Markdown a PDF"
        },
        {
            "role": "user",
            "content": markdown_content
        },
        {
            "role": "assistant",
            "content": "Contenido convertido correctamente a PDF."
        }
    ]
    return messages

def test_streamlit_cloud_conversion():
    """
    Prueba la conversión de Markdown a PDF utilizando el método
    optimizado para Streamlit Cloud.
    """
    # Crear directorio para los resultados si no existe
    output_dir = os.path.join(current_dir, "results")
    os.makedirs(output_dir, exist_ok=True)

    # Obtener la lista de archivos de muestra
    samples_dir = os.path.join(current_dir, "samples")
    sample_files = [f for f in os.listdir(samples_dir) if f.endswith('.md')]

    if not sample_files:
        logger.error(f"No se encontraron archivos Markdown en {samples_dir}")
        return

    # Ejecutar pruebas para cada archivo
    results = {}

    for sample_file in sample_files:
        sample_path = os.path.join(samples_dir, sample_file)
        sample_name = os.path.splitext(sample_file)[0]

        # Leer el contenido del archivo Markdown
        markdown_content = read_markdown_file(sample_path)
        if not markdown_content:
            continue

        logger.info(f"Probando conversión para: {sample_file}")

        # Preparar los mensajes para la conversión
        messages = format_markdown_as_messages(markdown_content)

        # Realizar la conversión
        try:
            start_time = datetime.now()
            pdf_content, _ = _export_chat_to_pdf_streamlit_cloud(messages)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Guardar el PDF resultante
            output_file = f"{sample_name}_streamlit_cloud.pdf"
            output_path = os.path.join(output_dir, output_file)
            success = save_pdf_file(pdf_content, output_path)

            if success:
                logger.info(f"Conversión exitosa en {duration:.2f} segundos")
                results[sample_name] = "Éxito"
            else:
                logger.error("Error al guardar el PDF")
                results[sample_name] = "Fallo al guardar"

        except Exception as e:
            logger.error(f"Error durante la conversión: {e}")
            results[sample_name] = f"Fallo: {str(e)}"

    # Mostrar resumen de resultados
    logger.info("\n=== RESUMEN DE RESULTADOS ===")
    for sample, result in results.items():
        logger.info(f"{sample}: {result}")

def check_wkhtmltopdf():
    """
    Verifica si wkhtmltopdf está instalado y disponible en el sistema.
    """
    logger.info("Verificando la disponibilidad de wkhtmltopdf...")

    try:
        # Intentar configurar pdfkit para usar wkhtmltopdf
        config = pdfkit.configuration()
        logger.info(f"wkhtmltopdf encontrado en: {config.wkhtmltopdf}")
        return True
    except Exception as e:
        logger.warning(f"No se pudo encontrar wkhtmltopdf: {e}")

        # Buscar wkhtmltopdf en ubicaciones comunes
        import platform
        system = platform.system().lower()

        if system == 'darwin':  # macOS
            possible_paths = [
                '/usr/local/bin/wkhtmltopdf',
                '/opt/homebrew/bin/wkhtmltopdf'
            ]
        elif system == 'linux':
            possible_paths = [
                '/usr/bin/wkhtmltopdf',
                '/usr/local/bin/wkhtmltopdf'
            ]
        else:  # Windows
            possible_paths = [
                'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
            ]

        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"wkhtmltopdf encontrado en: {path}")
                return True

        logger.error("wkhtmltopdf no encontrado. Por favor, instálalo para continuar.")
        logger.error("En macOS: brew install wkhtmltopdf")
        logger.error("En Linux: apt-get install wkhtmltopdf")
        logger.error("En Windows: Descarga e instala desde https://wkhtmltopdf.org/downloads.html")
        return False

if __name__ == "__main__":
    logger.info("Iniciando prueba de conversión optimizada para Streamlit Cloud")

    # Verificar wkhtmltopdf antes de continuar
    if check_wkhtmltopdf():
        test_streamlit_cloud_conversion()

    logger.info("Prueba completada")
