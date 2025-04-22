#!/bin/bash

# Script de configuración para Expert Nexus
# Este script detecta el sistema operativo, crea un entorno virtual,
# instala las dependencias y ejecuta la aplicación Streamlit

# Función para imprimir mensajes con colores
print_message() {
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo -e "$1"
    else
        echo -e "\033[1;34m$1\033[0m"
    fi
}

print_error() {
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo -e "$1"
    else
        echo -e "\033[1;31m$1\033[0m"
    fi
}

print_success() {
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo -e "$1"
    else
        echo -e "\033[1;32m$1\033[0m"
    fi
}

# Detectar sistema operativo
print_message "Detectando sistema operativo..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
    ACTIVATE_CMD="source venv/bin/activate"
    PYTHON_CMD="python3"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    OS="Windows"
    ACTIVATE_CMD="venv\\Scripts\\activate"
    PYTHON_CMD="python"
else
    OS="Linux"
    ACTIVATE_CMD="source venv/bin/activate"
    PYTHON_CMD="python3"
fi

print_success "Sistema operativo detectado: $OS"

# Detectar tipo de terminal
print_message "Detectando tipo de terminal..."
TERMINAL="Bash"
if [[ "$OS" == "Windows" ]]; then
    if [[ -n "$CMDER_ROOT" ]]; then
        TERMINAL="Cmder"
    elif [[ -n "$TERM_PROGRAM" && "$TERM_PROGRAM" == "vscode" ]]; then
        TERMINAL="VSCode"
    elif [[ -n "$WT_SESSION" ]]; then
        TERMINAL="Windows Terminal"
    elif [[ -n "$PROMPT" ]]; then
        TERMINAL="PowerShell"
    elif [[ -n "$BASH" ]]; then
        TERMINAL="Git Bash"
    else
        TERMINAL="CMD"
    fi
fi

print_success "Terminal detectada: $TERMINAL"

# Verificar si Python está instalado
print_message "Verificando instalación de Python..."
if ! command -v $PYTHON_CMD &> /dev/null; then
    print_error "Error: Python no está instalado o no se encuentra en el PATH."
    print_error "Por favor, instala Python 3.8 o superior desde https://www.python.org/downloads/"
    exit 1
fi

# Verificar versión de Python
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
print_success "Versión de Python: $PYTHON_VERSION"

# Verificar si la versión es compatible (3.8+)
if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l) -eq 1 ]]; then
    print_error "Error: Se requiere Python 3.8 o superior. Versión actual: $PYTHON_VERSION"
    print_error "Por favor, actualiza Python desde https://www.python.org/downloads/"
    exit 1
fi

# Crear entorno virtual
print_message "Creando entorno virtual..."
if [[ -d "venv" ]]; then
    print_message "El directorio 'venv' ya existe. ¿Deseas recrearlo? (s/n)"
    read -r response
    if [[ "$response" =~ ^([sS])$ ]]; then
        rm -rf venv
        $PYTHON_CMD -m venv venv
        if [ $? -ne 0 ]; then
            print_error "Error al crear el entorno virtual."
            exit 1
        fi
    fi
else
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        print_error "Error al crear el entorno virtual."
        exit 1
    fi
fi

print_success "Entorno virtual creado correctamente."

# Activar entorno virtual
print_message "Activando entorno virtual..."
if [[ "$OS" == "Windows" ]]; then
    if [[ "$TERMINAL" == "PowerShell" ]]; then
        # Para PowerShell, necesitamos ejecutar el script de activación de PowerShell
        print_message "Detectado PowerShell. Usando script de activación específico..."
        powershell -Command "& {. .\\venv\\Scripts\\Activate.ps1; exit \$LASTEXITCODE}"
    else
        # Para CMD, Git Bash, etc.
        . venv/Scripts/activate
    fi
else
    # Para macOS y Linux
    . venv/bin/activate
fi

if [ $? -ne 0 ]; then
    print_error "Error al activar el entorno virtual."
    print_message "Intenta activarlo manualmente:"
    if [[ "$OS" == "Windows" ]]; then
        print_message "  - CMD/Git Bash: venv\\Scripts\\activate"
        print_message "  - PowerShell: .\\venv\\Scripts\\Activate.ps1"
    else
        print_message "  - Bash/Zsh: source venv/bin/activate"
    fi
    exit 1
fi

print_success "Entorno virtual activado correctamente."

# Actualizar pip
print_message "Actualizando pip..."
if [[ "$OS" == "Windows" ]]; then
    python -m pip install --upgrade pip
else
    python3 -m pip install --upgrade pip
fi

if [ $? -ne 0 ]; then
    print_error "Error al actualizar pip."
    exit 1
fi

print_success "Pip actualizado correctamente."

# Instalar dependencias
print_message "Instalando dependencias desde requirements.txt..."
if [[ "$OS" == "Windows" ]]; then
    python -m pip install -r requirements.txt
else
    python3 -m pip install -r requirements.txt
fi

if [ $? -ne 0 ]; then
    print_error "Error al instalar dependencias."
    exit 1
fi

print_success "Dependencias instaladas correctamente."

# Ejecutar la aplicación
print_message "Iniciando la aplicación Streamlit..."
if [[ "$OS" == "Windows" ]]; then
    python -m streamlit run app.py
else
    python3 -m streamlit run app.py
fi

if [ $? -ne 0 ]; then
    print_error "Error al iniciar la aplicación Streamlit."
    exit 1
fi
