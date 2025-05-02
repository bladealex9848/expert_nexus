"""
Script para instalar las dependencias necesarias para las pruebas de Expert Nexus.
"""

import os
import sys
import subprocess
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - SETUP - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def install_dependencies():
    """Instala las dependencias necesarias para las pruebas."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_file = os.path.join(current_dir, "requirements.txt")
    
    if not os.path.exists(requirements_file):
        logging.error(f"No se encontró el archivo requirements.txt en {current_dir}")
        return False
    
    try:
        logging.info("Instalando dependencias...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        logging.info("Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error instalando dependencias: {str(e)}")
        return False

def main():
    # Mostrar banner
    print("\n" + "="*80)
    print("  EXPERT NEXUS - CONFIGURACIÓN DE PRUEBAS")
    print("="*80 + "\n")
    
    # Instalar dependencias
    if not install_dependencies():
        logging.error("No se pudieron instalar las dependencias. Abortando.")
        return
    
    # Verificar variables de entorno
    required_env_vars = ["OPENAI_API_KEY", "MISTRAL_API_KEY", "ASSISTANT_ID"]
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing_vars:
        logging.warning(f"Faltan variables de entorno: {', '.join(missing_vars)}")
        logging.info("Por favor, configura las siguientes variables de entorno:")
        for var in missing_vars:
            logging.info(f"  export {var}=tu_valor")
    else:
        logging.info("Variables de entorno configuradas correctamente")
    
    # Crear directorios necesarios
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dirs_to_create = ["test_files", "backups"]
    
    for dir_name in dirs_to_create:
        dir_path = os.path.join(current_dir, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        logging.info(f"Directorio creado: {dir_path}")
    
    # Mostrar instrucciones
    print("\n" + "="*80)
    print("  CONFIGURACIÓN COMPLETADA")
    print("="*80 + "\n")
    
    logging.info("Para ejecutar las pruebas:")
    logging.info("  python run_all.py")
    
    logging.info("\nPara ejecutar las pruebas e implementar soluciones automáticamente:")
    logging.info("  python run_all.py --implement")
    
    logging.info("\nPara más información, consulta el archivo README.md")

if __name__ == "__main__":
    main()
