"""
Punto de entrada principal para MDPDFusion.
"""

import sys
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mdpdfusion")

def main():
    """
    Función principal que determina qué interfaz iniciar según los argumentos.
    """
    # Verificar argumentos
    if len(sys.argv) > 1:
        # Si hay argumentos, usar la interfaz CLI
        from .cli import main as cli_main
        cli_main()
    else:
        # Sin argumentos, intentar iniciar la interfaz gráfica
        try:
            from .gui import main as gui_main
            gui_main()
        except ImportError:
            # Si no se puede importar PyQt5, usar la interfaz web
            try:
                from .web import main as web_main
                import streamlit
                print("Iniciando interfaz web con Streamlit...")
                print("Abre tu navegador en http://localhost:8501")
                # Streamlit requiere que se ejecute como un script separado
                import os
                import subprocess
                script_path = os.path.abspath(__file__)
                dir_path = os.path.dirname(script_path)
                web_script = os.path.join(dir_path, "web.py")
                subprocess.run([sys.executable, "-m", "streamlit", "run", web_script])
            except ImportError:
                logger.error("No se pudo iniciar ninguna interfaz. Asegúrate de tener instalado PyQt5 o Streamlit.")
                print("Error: No se pudo iniciar ninguna interfaz.")
                print("Uso: mdpdfusion [archivo.md ...]")
                sys.exit(1)

if __name__ == "__main__":
    main()
