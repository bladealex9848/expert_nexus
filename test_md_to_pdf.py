#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para la conversión de Markdown a PDF.
Este script prueba la conversión de archivos Markdown a PDF utilizando
el método optimizado para Streamlit Cloud.
"""

import os
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('md_to_pdf_test')

# Importar las funciones necesarias
try:
    from app import _export_chat_to_pdf_streamlit_cloud
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

def test_markdown_to_pdf_conversion():
    """
    Prueba la conversión de Markdown a PDF utilizando el método
    optimizado para Streamlit Cloud.
    """
    # Crear directorio para los resultados si no existe
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests", "conversion_results")
    os.makedirs(output_dir, exist_ok=True)

    # Definir archivos de prueba
    test_files = [
        {
            "name": "test_basic",
            "content": """
# Prueba Básica

Este es un documento de prueba básico para verificar la conversión de Markdown a PDF.

## Características

- Texto en **negrita**
- Texto en *cursiva*
- Lista numerada:
  1. Primer elemento
  2. Segundo elemento

## Código

```python
def hello_world():
    print("¡Hola, mundo!")
```

## Tabla

| Nombre | Edad |
|--------|------|
| Juan   | 30   |
| María  | 25   |
"""
        },
        {
            "name": "test_advanced",
            "content": """
# Prueba Avanzada

Este documento incluye características más avanzadas.

## Diagrama ASCII

```
+------------------+         +------------------+
|                  |         |                  |
|     Cliente      |-------->|     Servidor     |
|                  |         |                  |
+------------------+         +------------------+
```

## Bloques de código con sintaxis

```javascript
function calculateSum(a, b) {
  // Comentario
  return a + b;
}

const result = calculateSum(5, 3);
console.log(`El resultado es: ${result}`);
```

## Citas

> Esta es una cita.
>
> Puede tener múltiples párrafos.
"""
        }
    ]

    # Ejecutar pruebas para cada contenido
    results = {}

    for test_file in test_files:
        name = test_file["name"]
        content = test_file["content"]

        logger.info(f"Probando conversión para: {name}")

        # Preparar los mensajes para la conversión
        messages = format_markdown_as_messages(content)

        # Realizar la conversión
        try:
            # Primero intentamos con el método optimizado para Streamlit Cloud
            start_time = datetime.now()
            try:
                pdf_content, _ = _export_chat_to_pdf_streamlit_cloud(messages)
                logger.info("Conversión exitosa con método Streamlit Cloud")
            except Exception as e:
                logger.warning(f"Error con método Streamlit Cloud: {str(e)}")

                # Si falla, intentamos con el método primario (FPDF)
                try:
                    from app import _export_chat_to_pdf_primary
                    pdf_content, _ = _export_chat_to_pdf_primary(messages)
                    logger.info("Conversión exitosa con método FPDF")
                except Exception as e2:
                    logger.warning(f"Error con método FPDF: {str(e2)}")

                    # Si falla, intentamos con el método secundario (ReportLab)
                    try:
                        from app import _export_chat_to_pdf_secondary
                        pdf_content, _ = _export_chat_to_pdf_secondary(messages)
                        logger.info("Conversión exitosa con método ReportLab")
                    except Exception as e3:
                        logger.warning(f"Error con método ReportLab: {str(e3)}")

                        # Si todo falla, usamos el método de respaldo
                        from app import _export_chat_to_pdf_fallback
                        pdf_content, _ = _export_chat_to_pdf_fallback(messages)
                        logger.info("Conversión exitosa con método de respaldo")

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Guardar el PDF resultante
            output_file = f"{name}.pdf"
            output_path = os.path.join(output_dir, output_file)
            success = save_pdf_file(pdf_content, output_path)

            # También guardar el archivo Markdown para comparación
            md_path = os.path.join(output_dir, f"{name}.md")
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(content)

            if success:
                logger.info(f"Conversión exitosa en {duration:.2f} segundos")
                results[name] = {
                    "status": "Éxito",
                    "duration": f"{duration:.2f} segundos",
                    "pdf_path": output_path,
                    "md_path": md_path
                }
            else:
                logger.error("Error al guardar el PDF")
                results[name] = {"status": "Fallo al guardar"}

        except Exception as e:
            logger.error(f"Error durante la conversión: {e}")
            results[name] = {"status": f"Fallo: {str(e)}"}

    # Mostrar resumen de resultados
    logger.info("\n=== RESUMEN DE RESULTADOS ===")
    for name, result in results.items():
        status = result["status"]
        logger.info(f"{name}: {status}")

        if "pdf_path" in result:
            logger.info(f"  - PDF: {result['pdf_path']}")
            logger.info(f"  - MD: {result['md_path']}")

    # Devolver rutas de los archivos generados
    return results

if __name__ == "__main__":
    logger.info("Iniciando prueba de conversión de Markdown a PDF")

    # Activar entorno virtual si no está activado
    if not os.environ.get('VIRTUAL_ENV'):
        logger.warning("Entorno virtual no activado. Algunas dependencias podrían no estar disponibles.")

    # Ejecutar prueba
    results = test_markdown_to_pdf_conversion()

    # Mostrar instrucciones para ver los resultados
    if any("pdf_path" in result for result in results.values()):
        logger.info("\nPara ver los resultados, abra los archivos PDF generados en la carpeta 'tests/conversion_results'")
        logger.info("Compare los archivos PDF con los archivos MD correspondientes para verificar la fidelidad de la conversión")

    logger.info("Prueba completada")
