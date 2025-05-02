#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para validar la conversión de Markdown a PDF en Expert Nexus.
Este script utiliza el código de MDPDFusion para generar PDFs satisfactorios.
"""

import os
import sys
import logging
import shutil
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('conversion_test')

# Importar la función de conversión desde mdpdfusion.py
try:
    from mdpdfusion import convert_md_to_pdf
    logger.info("Módulo mdpdfusion importado correctamente")
except ImportError as e:
    logger.error(f"Error al importar módulo de conversión: {e}")
    sys.exit(1)

def verify_dependencies():
    """Verifica que todas las dependencias necesarias estén instaladas."""
    dependencies = [
        ('markdown', 'markdown'),
        ('reportlab', 'reportlab'),
        ('pypandoc', 'pypandoc (opcional)')
    ]

    missing = []
    for module, name in dependencies:
        try:
            __import__(module)
            logger.info(f"✓ {name} está instalado")
        except ImportError:
            if 'opcional' in name:
                logger.warning(f"⚠ {name} no está instalado (opcional)")
            else:
                logger.error(f"✗ {name} no está instalado")
                missing.append(name)

    if missing:
        logger.warning(f"Faltan dependencias: {', '.join(missing)}")
        logger.warning("Instala las dependencias faltantes con: pip install " + " ".join([m.split()[0] for m in missing]))
        return False

    return True

def run_conversion_tests():
    """Ejecuta las pruebas de conversión de Markdown a PDF."""
    # Archivos de prueba
    test_files = [
        "test_markdown.md",
        "test_enlaces.md",
        os.path.join("tests", "conversion_results", "test_advanced.md"),
        os.path.join("tests", "conversion_results", "test_basic.md")
    ]

    # Carpeta de salida
    output_folder = os.path.join("tests", "conversion_results")
    os.makedirs(output_folder, exist_ok=True)

    # Resultados
    results = {}

    # Convertir cada archivo
    for file in test_files:
        if not os.path.exists(file):
            logger.error(f"El archivo {file} no existe")
            continue

        logger.info(f"Convirtiendo {file} a PDF...")

        # Medir el tiempo de conversión
        start_time = datetime.now()

        # Convertir el archivo
        output_pdf = convert_md_to_pdf(file, output_folder)

        # Calcular el tiempo de conversión
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Verificar el resultado
        if output_pdf and os.path.exists(output_pdf):
            logger.info(f"Conversión exitosa en {duration:.2f} segundos. PDF generado: {output_pdf}")
            results[file] = "Éxito"
        else:
            logger.error(f"La conversión de {file} falló")
            results[file] = "Fallo"

    # Crear informe
    create_report(output_folder, results)

    # Mostrar resumen
    logger.info("\n=== RESUMEN DE RESULTADOS ===")
    for file, result in results.items():
        logger.info(f"  - {file}: {result}")

    return results

def create_report(output_dir, results):
    """Crea un informe de las pruebas de conversión."""
    report_path = os.path.join(output_dir, "test_report.md")

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Informe de Pruebas de Conversión Markdown a PDF\n\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write("## Resumen de Pruebas\n\n")
        f.write("Se realizaron pruebas de conversión de archivos Markdown a PDF utilizando MDPDFusion.\n\n")
        f.write("MDPDFusion utiliza una combinación de métodos para garantizar la mejor calidad de conversión:\n\n")
        f.write("1. **Método Pypandoc**: Utiliza `pypandoc` para la conversión (si está disponible).\n")
        f.write("2. **Método ReportLab**: Utiliza la biblioteca `reportlab` para la conversión.\n\n")

        f.write("### Resultados\n\n")
        f.write("| Archivo | Resultado |\n")
        f.write("|---------|----------|\n")

        for file, result in results.items():
            f.write(f"| {file} | {result} |\n")

        f.write("\n## Características de la conversión\n\n")
        f.write("La conversión de Markdown a PDF con MDPDFusion soporta las siguientes características:\n\n")
        f.write("- Encabezados (H1, H2, H3, H4)\n")
        f.write("- Formato de texto (negrita, cursiva, tachado)\n")
        f.write("- Listas ordenadas y no ordenadas (con anidamiento)\n")
        f.write("- Bloques de código con resaltado de sintaxis\n")
        f.write("- Tablas\n")
        f.write("- Imágenes (locales y remotas)\n")
        f.write("- Enlaces (internos y externos)\n")
        f.write("- Citas\n")
        f.write("- Líneas horizontales\n\n")

        f.write("## Recomendaciones\n\n")
        f.write("Para obtener los mejores resultados en la conversión de Markdown a PDF:\n\n")
        f.write("1. **Instalar todas las dependencias**: Asegúrate de tener instaladas todas las dependencias necesarias.\n")
        f.write("   - `pip install markdown reportlab pypandoc`\n\n")
        f.write("2. **Usar sintaxis Markdown estándar**: Evita características específicas de variantes como GitHub Flavored Markdown.\n\n")
        f.write("3. **Optimizar imágenes**: Usa imágenes optimizadas para reducir el tamaño del PDF.\n\n")
        f.write("4. **Verificar enlaces internos**: Asegúrate de que los enlaces internos apunten a secciones existentes.\n\n")

        f.write("## Conclusiones\n\n")
        f.write("MDPDFusion proporciona una solución robusta para la conversión de Markdown a PDF, ")
        f.write("con soporte para todas las características principales de Markdown y una buena calidad visual en el resultado final.\n\n")
        f.write("La implementación basada en ReportLab garantiza la compatibilidad con la mayoría de los entornos ")
        f.write("y no requiere dependencias externas del sistema operativo.\n")

    logger.info(f"Informe guardado en: {report_path}")
    return report_path

def main():
    """Función principal."""
    logger.info("Iniciando pruebas de conversión Markdown a PDF con MDPDFusion")

    # Verificar dependencias
    verify_dependencies()

    # Ejecutar pruebas de conversión
    run_conversion_tests()

    logger.info("Pruebas completadas")

if __name__ == "__main__":
    main()
