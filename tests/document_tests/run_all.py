"""
Script principal para ejecutar todo el proceso de prueba, análisis e implementación
de soluciones para el procesamiento de documentos en Expert Nexus.
"""

import os
import sys
import logging
import argparse
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - RUN_ALL - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Verificar variables de entorno necesarias
required_env_vars = ["OPENAI_API_KEY", "MISTRAL_API_KEY", "ASSISTANT_ID"]
missing_vars = [var for var in required_env_vars if not os.environ.get(var)]

if missing_vars:
    logging.error(f"Faltan variables de entorno: {', '.join(missing_vars)}")
    logging.info("Por favor, configura las variables de entorno antes de ejecutar la prueba:")
    for var in missing_vars:
        logging.info(f"  export {var}=tu_valor")
    sys.exit(1)

def run_script(script_name, description):
    """Ejecuta un script Python y devuelve True si se ejecutó correctamente."""
    logging.info(f"Ejecutando: {description}...")
    try:
        # Importar y ejecutar el script
        module_name = script_name.replace(".py", "")
        __import__(module_name)
        logging.info(f"✅ {description} completado con éxito")
        return True
    except Exception as e:
        logging.error(f"❌ Error en {description}: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return False

def main():
    # Parsear argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Ejecutar pruebas y soluciones para Expert Nexus")
    parser.add_argument("--test-only", action="store_true", help="Ejecutar solo las pruebas sin implementar soluciones")
    parser.add_argument("--implement", action="store_true", help="Implementar soluciones automáticamente")
    args = parser.parse_args()
    
    # Mostrar banner
    print("\n" + "="*80)
    print("  EXPERT NEXUS - PRUEBAS DE PROCESAMIENTO DE DOCUMENTOS")
    print("="*80 + "\n")
    
    # Crear directorio para archivos de prueba
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_files_dir = os.path.join(current_dir, "test_files")
    os.makedirs(test_files_dir, exist_ok=True)
    
    # Ejecutar pruebas
    if not run_script("run_document_test.py", "Pruebas de procesamiento de documentos"):
        logging.error("Las pruebas fallaron. Abortando.")
        return
    
    # Esperar un momento para asegurarse de que los archivos se han guardado
    time.sleep(1)
    
    # Analizar resultados
    if not run_script("analyze_results.py", "Análisis de resultados"):
        logging.error("El análisis falló. Abortando.")
        return
    
    # Implementar soluciones si se solicita
    if args.implement:
        if not run_script("implement_solutions.py", "Implementación de soluciones"):
            logging.error("La implementación falló.")
            return
        
        logging.info("\n✅ Proceso completo ejecutado con éxito")
        logging.info("Se recomienda reiniciar la aplicación para aplicar los cambios")
    elif not args.test_only:
        logging.info("\n✅ Pruebas y análisis completados con éxito")
        logging.info("Para implementar las soluciones automáticamente, ejecuta:")
        logging.info("  python run_all.py --implement")
    else:
        logging.info("\n✅ Pruebas completadas con éxito")
    
    # Mostrar ubicación de los resultados
    solutions_file = os.path.join(test_files_dir, "solutions_report.md")
    if os.path.exists(solutions_file):
        logging.info(f"\nPuedes ver el informe de soluciones en: {solutions_file}")

if __name__ == "__main__":
    main()
