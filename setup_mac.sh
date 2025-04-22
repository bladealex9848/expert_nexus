#!/bin/bash

# Script de configuración para Expert Nexus en macOS/Linux
# Este script crea un entorno virtual, instala las dependencias y ejecuta la aplicación Streamlit

# Función para imprimir mensajes con colores
print_message() {
    echo -e "\033[1;34m$1\033[0m"
}

print_error() {
    echo -e "\033[1;31m$1\033[0m"
}

print_success() {
    echo -e "\033[1;32m$1\033[0m"
}

# Verificar si Python está instalado
print_message "Verificando instalación de Python..."
if ! command -v python3 &> /dev/null; then
    print_error "Error: Python no está instalado o no se encuentra en el PATH."
    print_error "Por favor, instala Python 3.8 o superior."
    exit 1
fi

# Verificar versión de Python
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
print_success "Versión de Python: $PYTHON_VERSION"

# Verificar si la versión es compatible (3.8+)
if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l) -eq 1 ]]; then
    print_error "Error: Se requiere Python 3.8 o superior. Versión actual: $PYTHON_VERSION"
    print_error "Por favor, actualiza Python."
    exit 1
fi

# Crear entorno virtual
print_message "Creando entorno virtual..."
if [[ -d "venv" ]]; then
    print_message "El directorio 'venv' ya existe. ¿Deseas recrearlo? (s/n)"
    read -r response
    if [[ "$response" =~ ^([sS])$ ]]; then
        rm -rf venv
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            print_error "Error al crear el entorno virtual."
            exit 1
        fi
    fi
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_error "Error al crear el entorno virtual."
        exit 1
    fi
fi

print_success "Entorno virtual creado correctamente."

# Activar entorno virtual
print_message "Activando entorno virtual..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    print_error "Error al activar el entorno virtual."
    print_message "Intenta activarlo manualmente: source venv/bin/activate"
    exit 1
fi

print_success "Entorno virtual activado correctamente."

# Actualizar pip
print_message "Actualizando pip..."
python3 -m pip install --upgrade pip

if [ $? -ne 0 ]; then
    print_error "Error al actualizar pip."
    exit 1
fi

print_success "Pip actualizado correctamente."

# Instalar dependencias
print_message "Instalando dependencias desde requirements.txt..."
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    print_error "Error al instalar dependencias."
    exit 1
fi

print_success "Dependencias instaladas correctamente."

# Ejecutar la aplicación
print_message "Iniciando la aplicación Streamlit..."
python3 -m streamlit run app.py

if [ $? -ne 0 ]; then
    print_error "Error al iniciar la aplicación Streamlit."
    exit 1
fi
