#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script principal para ejecutar todas las pruebas de conversión de Markdown a PDF.
"""

import os
import sys
import logging
import subprocess
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('conversion_tests.log')
    ]
)
logger = logging.getLogger('run_tests')

def run_test_script(script_path):
    """Ejecuta un script de prueba y devuelve su salida."""
    logger.info(f"Ejecutando script: {os.path.basename(script_path)}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Script ejecutado correctamente: {os.path.basename(script_path)}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al ejecutar el script {os.path.basename(script_path)}: {e}")
        logger.error(f"Salida de error: {e.stderr}")
        return False, e.stderr

def generate_report(results):
    """Genera un informe de las pruebas realizadas."""
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "test_report.md")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Informe de Pruebas de Conversión Markdown a PDF\n\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Resumen de Pruebas\n\n")
        
        for script_name, (success, _) in results.items():
            status = "✅ Éxito" if success else "❌ Fallo"
            f.write(f"- **{script_name}**: {status}\n")
        
        f.write("\n## Detalles de las Pruebas\n\n")
        
        for script_name, (success, output) in results.items():
            f.write(f"### {script_name}\n\n")
            f.write(f"Estado: {'Éxito' if success else 'Fallo'}\n\n")
            f.write("```\n")
            f.write(output[:2000] + "..." if len(output) > 2000 else output)
            f.write("\n```\n\n")
        
        f.write("## Archivos PDF Generados\n\n")
        
        results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
        pdf_files = [f for f in os.listdir(results_dir) if f.endswith('.pdf')]
        
        for pdf_file in pdf_files:
            f.write(f"- {pdf_file}\n")
    
    logger.info(f"Informe generado en: {report_path}")
    return report_path

def main():
    """Función principal para ejecutar todas las pruebas."""
    logger.info("Iniciando ejecución de pruebas de conversión")
    
    # Obtener la ruta del directorio actual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Crear directorio para los resultados si no existe
    results_dir = os.path.join(current_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Lista de scripts de prueba a ejecutar
    test_scripts = [
        os.path.join(current_dir, "test_streamlit_cloud_conversion.py"),
        os.path.join(current_dir, "test_conversion.py")
    ]
    
    # Ejecutar cada script y recopilar resultados
    results = {}
    
    for script_path in test_scripts:
        script_name = os.path.basename(script_path)
        success, output = run_test_script(script_path)
        results[script_name] = (success, output)
    
    # Generar informe de resultados
    report_path = generate_report(results)
    
    # Mostrar resumen final
    logger.info("\n=== RESUMEN FINAL ===")
    for script_name, (success, _) in results.items():
        logger.info(f"{script_name}: {'Éxito' if success else 'Fallo'}")
    
    logger.info(f"Informe detallado disponible en: {report_path}")
    logger.info("Pruebas completadas")

if __name__ == "__main__":
    main()
