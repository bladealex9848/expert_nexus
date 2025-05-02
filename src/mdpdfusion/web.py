"""
Módulo para la interfaz web de MDPDFusion usando Streamlit.
"""

import os
import logging
import traceback
import tempfile
import streamlit as st
from .core import convert_md_to_pdf

# Configurar logging
logger = logging.getLogger("mdpdfusion.web")

def main():
    """Función principal para la interfaz web de Streamlit."""
    try:
        st.title("MDPDFusion: Convertidor de Markdown a PDF")

        # Selección de archivos MD
        md_files = st.file_uploader("Selecciona los archivos Markdown (.md)", type=['md'], accept_multiple_files=True)

        if md_files:
            # Crear una carpeta temporal para los archivos de salida
            with tempfile.TemporaryDirectory() as output_folder:
                for md_file in md_files:
                    # Guardar el archivo subido temporalmente
                    temp_md_path = os.path.join(output_folder, md_file.name)
                    with open(temp_md_path, 'wb') as temp_file:
                        temp_file.write(md_file.getvalue())

                    # Convertir MD a PDF
                    pdf_path = convert_md_to_pdf(temp_md_path, output_folder)

                    if pdf_path and os.path.exists(pdf_path):
                        # Ofrecer el archivo PDF para descarga
                        with open(pdf_path, 'rb') as pdf_file:
                            st.download_button(
                                label=f"Descargar {os.path.basename(pdf_path)}",
                                data=pdf_file,
                                file_name=os.path.basename(pdf_path),
                                mime="application/pdf"
                            )
                    else:
                        st.error(f"No se pudo convertir {md_file.name} a PDF. Por favor, revisa el archivo de entrada.")
    except Exception as e:
        st.error(f"Error inesperado: {str(e)}")
        logger.error(f"Error inesperado en main: {str(e)}")
        logger.error(traceback.format_exc())
