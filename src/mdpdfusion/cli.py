"""
Módulo para la interfaz de línea de comandos de MDPDFusion.
"""

import os
import sys
import argparse
import logging
from .core import convert_md_to_pdf

# Configurar logging
logger = logging.getLogger("mdpdfusion.cli")

def main():
    """Función principal del CLI"""
    # Crear el parser de argumentos
    parser = argparse.ArgumentParser(
        description='Convierte archivos Markdown a PDF',
        epilog='Ejemplo: mdpdfusion archivo.md'
    )
    
    # Añadir argumentos
    parser.add_argument(
        'files', 
        metavar='archivo.md', 
        type=str, 
        nargs='+',
        help='Archivos Markdown a convertir'
    )
    
    parser.add_argument(
        '-o', '--output-dir', 
        dest='output_dir',
        help='Directorio de salida para los PDFs (por defecto: mismo directorio que el archivo MD)'
    )
    
    parser.add_argument(
        '-v', '--verbose', 
        action='store_true',
        help='Mostrar información detallada durante la conversión'
    )
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Configurar nivel de logging según verbose
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Modo verbose activado")
    
    # Procesar cada archivo
    for md_file in args.files:
        if not os.path.exists(md_file):
            logger.error(f"El archivo {md_file} no existe")
            continue
        
        if not md_file.lower().endswith('.md'):
            logger.warning(f"El archivo {md_file} no parece ser un archivo Markdown (.md)")
            continue
        
        # Determinar directorio de salida
        if args.output_dir:
            output_dir = args.output_dir
            # Crear el directorio si no existe
            os.makedirs(output_dir, exist_ok=True)
        else:
            # Usar el mismo directorio que el archivo de entrada
            output_dir = os.path.dirname(md_file)
            if not output_dir:  # Si es un archivo en el directorio actual
                output_dir = '.'
        
        logger.info(f"Convirtiendo {md_file} a PDF...")
        try:
            output_pdf = convert_md_to_pdf(md_file, output_dir)
            
            if output_pdf and os.path.exists(output_pdf):
                logger.info(f"Conversión exitosa. PDF generado: {output_pdf}")
            else:
                logger.error(f"La conversión de {md_file} falló")
        except Exception as e:
            logger.error(f"Error al convertir {md_file}: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Error crítico: {str(e)}")
        sys.exit(1)
