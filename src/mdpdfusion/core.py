"""
Módulo principal de MDPDFusion que contiene las funciones de conversión.
"""

import os
import logging
import traceback
import tempfile
from .formatters import process_inline_formatting
from .converters import convert_with_pypandoc, convert_with_reportlab

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mdpdfusion")

def convert_md_to_pdf(md_file, output_folder):
    """
    Convierte un archivo Markdown a PDF.
    
    Args:
        md_file (str): Ruta al archivo Markdown a convertir
        output_folder (str): Directorio donde se guardará el PDF generado
        
    Returns:
        str: Ruta al archivo PDF generado, o None si la conversión falló
    """
    try:
        # Leer el contenido del archivo MD
        with open(md_file, 'r', encoding='utf-8') as file:
            md_content = file.read()

        # Preparar el nombre del archivo de salida
        output_pdf = os.path.join(output_folder, os.path.splitext(os.path.basename(md_file))[0] + '.pdf')

        # Intentar conversión con pypandoc
        if convert_with_pypandoc(md_content, output_pdf):
            logger.info("Conversión exitosa con pypandoc")
            return output_pdf

        # Si falla, usar reportlab como última opción
        try:
            if convert_with_reportlab(md_content, output_pdf):
                logger.info("Conversión exitosa con reportlab")
                return output_pdf
        except ValueError as ve:
            # Manejar específicamente errores de enlaces
            if "format not resolved" in str(ve) and "missing URL scheme or undefined destination target" in str(ve):
                target = str(ve).split("'")[-2] if "'" in str(ve) else "desconocido"
                logger.error(f"Error en enlaces internos: No se pudo resolver el enlace a '{target}'. "
                            f"Esto puede ocurrir cuando un enlace apunta a una sección que no existe o tiene formato incorrecto.")
                # Intentar nuevamente con una versión modificada que ignore enlaces problemáticos
                try:
                    # Modificar el contenido para marcar los enlaces problemáticos
                    modified_content = md_content.replace(f"(#{target})", f"(#ERROR-ENLACE-{target})")
                    if convert_with_reportlab(modified_content, output_pdf):
                        logger.warning(f"Conversión completada con advertencias: Algunos enlaces internos pueden no funcionar correctamente.")
                        return output_pdf
                except Exception as retry_error:
                    logger.error(f"Error en segundo intento: {str(retry_error)}")
            else:
                # Otros errores de ValueError
                logger.error(f"Error de valor en la conversión: {str(ve)}")
        except Exception as e:
            # Otros errores en reportlab
            logger.error(f"Error en la conversión con reportlab: {str(e)}")
            traceback.print_exc()

        # Si todas las conversiones fallan, registrar un error
        logger.error("Todas las conversiones fallaron")
        return None
    except Exception as e:
        logger.error(f"Error inesperado en convert_md_to_pdf: {str(e)}")
        traceback.print_exc()
        return None
