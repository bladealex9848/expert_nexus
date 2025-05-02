#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para validar la conversión de Markdown a PDF en Expert Nexus.
Este script prueba diferentes métodos de conversión y genera archivos PDF para su inspección visual.
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
logger = logging.getLogger('conversion_test')

# Añadir el directorio raíz al path para importar módulos de la aplicación
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, root_dir)
print(f"Directorio raíz: {root_dir}")

# Importar las funciones de conversión de la aplicación
try:
    from app import _export_chat_to_pdf_streamlit_cloud, _export_chat_to_pdf_primary, _export_chat_to_pdf_secondary, _export_chat_to_pdf_fallback
    from app import export_chat_to_markdown
except ImportError as e:
    logger.error(f"Error al importar módulos de la aplicación: {e}")
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

def test_conversion_method(method_name, conversion_func, markdown_content, output_path):
    """Prueba un método específico de conversión de Markdown a PDF."""
    logger.info(f"Probando método de conversión: {method_name}")

    try:
        # Preparar los mensajes para la conversión
        messages = format_markdown_as_messages(markdown_content)

        # Realizar la conversión
        start_time = datetime.now()

        if method_name == "markdown_to_pdf":
            # Este método espera directamente el contenido markdown
            pdf_content, _ = conversion_func(messages)
        else:
            # Primero convertir a markdown y luego a PDF
            md_content = export_chat_to_markdown(messages)
            temp_messages = format_markdown_as_messages(md_content)
            pdf_content, _ = conversion_func(temp_messages)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Guardar el PDF resultante
        success = save_pdf_file(pdf_content, output_path)

        if success:
            logger.info(f"Conversión exitosa con {method_name} en {duration:.2f} segundos")
            return True
        else:
            logger.error(f"Error al guardar el PDF con {method_name}")
            return False

    except Exception as e:
        logger.error(f"Error durante la conversión con {method_name}: {e}")
        return False

def run_all_tests():
    """Ejecuta todas las pruebas de conversión."""
    # Crear directorio para los resultados si no existe
    output_dir = os.path.join(current_dir, "results")
    os.makedirs(output_dir, exist_ok=True)

    # Obtener la lista de archivos de muestra
    samples_dir = os.path.join(current_dir, "samples")
    sample_files = [f for f in os.listdir(samples_dir) if f.endswith('.md')]

    if not sample_files:
        logger.error(f"No se encontraron archivos Markdown en {samples_dir}")
        return

    # Métodos de conversión a probar
    conversion_methods = [
        ("streamlit_cloud", _export_chat_to_pdf_streamlit_cloud),
        ("primary", _export_chat_to_pdf_primary),
        ("secondary", _export_chat_to_pdf_secondary),
        ("fallback", _export_chat_to_pdf_fallback)
    ]

    # Ejecutar pruebas para cada archivo y método
    results = {}

    for sample_file in sample_files:
        sample_path = os.path.join(samples_dir, sample_file)
        sample_name = os.path.splitext(sample_file)[0]

        # Leer el contenido del archivo Markdown
        markdown_content = read_markdown_file(sample_path)
        if not markdown_content:
            continue

        logger.info(f"Probando conversión para: {sample_file}")

        # Probar cada método de conversión
        for method_name, conversion_func in conversion_methods:
            output_file = f"{sample_name}_{method_name}.pdf"
            output_path = os.path.join(output_dir, output_file)

            success = test_conversion_method(
                method_name,
                conversion_func,
                markdown_content,
                output_path
            )

            # Almacenar resultado
            if sample_name not in results:
                results[sample_name] = {}
            results[sample_name][method_name] = "Éxito" if success else "Fallo"

    # Mostrar resumen de resultados
    logger.info("\n=== RESUMEN DE RESULTADOS ===")
    for sample, methods in results.items():
        logger.info(f"\nArchivo: {sample}")
        for method, result in methods.items():
            logger.info(f"  - {method}: {result}")

if __name__ == "__main__":
    logger.info("Iniciando pruebas de conversión de Markdown a PDF")
    run_all_tests()
    logger.info("Pruebas completadas")
