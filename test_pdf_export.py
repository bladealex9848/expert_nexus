#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para validar la exportación a PDF en Expert Nexus.
Este script prueba la función export_chat_to_pdf con MDPDFusion.
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
logger = logging.getLogger('pdf_export_test')

# Importar la función de exportación a Markdown
try:
    from app import export_chat_to_markdown
    logger.info("Función export_chat_to_markdown importada correctamente")
except ImportError as e:
    logger.error(f"Error al importar función de exportación: {e}")
    sys.exit(1)

# Importar la función de conversión de MDPDFusion
try:
    from mdpdfusion import convert_md_to_pdf
    logger.info("Función convert_md_to_pdf importada correctamente")
except ImportError as e:
    logger.error(f"Error al importar función de conversión: {e}")
    sys.exit(1)

def test_pdf_export():
    """Prueba la exportación a PDF utilizando MDPDFusion directamente."""
    # Crear mensajes de prueba
    messages = [
        {"role": "system", "content": "Bienvenido a Expert Nexus."},
        {"role": "user", "content": "Hola, ¿cómo estás?"},
        {"role": "assistant", "content": "Estoy bien, gracias por preguntar. ¿En qué puedo ayudarte hoy?"},
        {"role": "user", "content": "Quiero saber más sobre la conversión de Markdown a PDF."},
        {"role": "assistant", "content": """
# Conversión de Markdown a PDF

La conversión de Markdown a PDF es un proceso que permite transformar documentos escritos en formato Markdown a documentos PDF.

## Ventajas

- **Facilidad de escritura**: Markdown es un formato sencillo de escribir.
- **Formato visual**: El PDF resultante tiene un formato visual profesional.
- **Portabilidad**: Los archivos PDF son compatibles con prácticamente cualquier dispositivo.

## Métodos de conversión

Existen varios métodos para convertir Markdown a PDF:

1. **Usando MDPDFusion**: Una biblioteca especializada para la conversión.
2. **Usando Pandoc**: Una herramienta de línea de comandos muy potente.
3. **Usando WeasyPrint**: Una biblioteca de Python para generar PDF a partir de HTML.

## Ejemplo de tabla

| Método | Ventajas | Desventajas |
|--------|----------|-------------|
| MDPDFusion | Fácil de usar, buena calidad | Requiere dependencias |
| Pandoc | Muy potente, muchas opciones | Más complejo de configurar |
| WeasyPrint | Buena calidad visual | Dependencias del sistema |

## Conclusión

La elección del método dependerá de tus necesidades específicas y del entorno en el que estés trabajando.
        """}
    ]

    # Carpeta de salida
    output_dir = "tests/pdf_export_results"
    os.makedirs(output_dir, exist_ok=True)

    # Exportar a Markdown
    logger.info("Exportando mensajes a Markdown...")
    md_content = export_chat_to_markdown(messages)
    md_path = os.path.join(output_dir, "test_export.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    logger.info(f"Markdown guardado en: {md_path}")

    # Convertir Markdown a PDF usando MDPDFusion directamente
    logger.info("Convirtiendo Markdown a PDF con MDPDFusion...")
    try:
        output_pdf = convert_md_to_pdf(md_path, output_dir)
        
        if output_pdf and os.path.exists(output_pdf):
            logger.info(f"PDF generado exitosamente: {output_pdf}")
            return True
        else:
            logger.error("La conversión no generó un archivo PDF válido")
            return False
    except Exception as e:
        logger.error(f"Error durante la conversión a PDF: {e}")
        return False

def main():
    """Función principal."""
    logger.info("Iniciando prueba de exportación a PDF")
    
    success = test_pdf_export()
    
    if success:
        logger.info("Prueba completada con éxito")
    else:
        logger.error("La prueba falló")
        sys.exit(1)

if __name__ == "__main__":
    main()
