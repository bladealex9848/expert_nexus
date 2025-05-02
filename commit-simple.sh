#!/bin/bash

# Obtener la fecha y hora actual en formato español
FECHA_HORA=$(date "+%d/%m/%Y %H:%M:%S")

# Si no se proporciona un mensaje de commit, usar uno estándar con la fecha y hora
if [ -z "$1" ]; then
    COMMIT_MESSAGE="Actualización automática del $FECHA_HORA"
else
    COMMIT_MESSAGE="$1"
fi

# Colores para los mensajes
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Ejecutar los comandos de Git
echo -e "${CYAN}Añadiendo todos los cambios al área de preparación...${NC}"
git add .

echo -e "${GREEN}Realizando commit con el mensaje: '$COMMIT_MESSAGE'...${NC}"
git commit -m "$COMMIT_MESSAGE" --no-verify

echo -e "${YELLOW}Subiendo cambios a la rama clean-branch...${NC}"
git push origin clean-branch --no-verify

echo -e "${MAGENTA}¡Proceso completado con éxito!${NC}"
