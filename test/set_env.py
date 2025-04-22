"""
Script para configurar las variables de entorno necesarias para las pruebas.
"""

import os
import sys

# Configurar variables de entorno
# Nota: Las claves API deben configurarse antes de ejecutar este script
# a través de variables de entorno del sistema o secrets.toml
os.environ.setdefault("OPENAI_API_KEY", "")
os.environ.setdefault("MISTRAL_API_KEY", "")
os.environ.setdefault("ASSISTANT_ID", "asst_RfRNo5Ij76ieg7mV11CqYV9v")

print("Variables de entorno configuradas correctamente")

# Ejecutar el script especificado como argumento
if len(sys.argv) > 1:
    script_to_run = sys.argv[1]
    print("Ejecutando script especificado")
    exec(open(script_to_run).read())
