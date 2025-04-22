@echo off
REM Script de configuración para Expert Nexus en Windows
REM Este script crea un entorno virtual, instala las dependencias y ejecuta la aplicación Streamlit

echo Iniciando configuración de Expert Nexus...

REM Verificar si Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python no está instalado o no se encuentra en el PATH.
    echo Por favor, instala Python 3.8 o superior desde https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Verificar versión de Python
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set PYTHON_VERSION=%%I
echo Versión de Python: %PYTHON_VERSION%

REM Crear entorno virtual
if exist venv (
    echo El directorio 'venv' ya existe. ¿Deseas recrearlo? (S/N)
    set /p RECREATE=
    if /i "%RECREATE%"=="S" (
        echo Eliminando entorno virtual existente...
        rmdir /s /q venv
        echo Creando nuevo entorno virtual...
        python -m venv venv
    )
) else (
    echo Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat

REM Actualizar pip
echo Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias
echo Instalando dependencias desde requirements.txt...
python -m pip install -r requirements.txt

REM Ejecutar la aplicación
echo Iniciando la aplicación Streamlit...
python -m streamlit run app.py

pause
