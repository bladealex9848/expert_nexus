# Registro de Cambios (Changelog)

Todos los cambios notables en el proyecto Expert Nexus serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-05-01

### Añadido
- Soporte para archivos Markdown (.md) como formato de entrada
- Función para procesar archivos Markdown y extraer su contenido como texto
- Exportación avanzada de conversaciones en formato PDF usando WeasyPrint
- Visualización mejorada de archivos Markdown en la interfaz de usuario
- Módulo `expert_selection.py` para gestionar la selección y cambio de expertos
- Soporte para resaltado de sintaxis en bloques de código en la exportación a PDF
- Preservación de diagramas ASCII en la exportación a PDF
- Estilos mejorados para tablas, listas y otros elementos en la exportación a PDF

### Modificado
- Actualizado el sistema de exportación para soportar tanto Markdown como PDF
- Mejorada la visualización de contenido de archivos en los mensajes
- Actualizado `requirements.txt` con nuevas dependencias para la conversión de Markdown a PDF
- Actualizado README.md con información sobre las nuevas funcionalidades
- Mejorada la compatibilidad de la exportación a PDF con Streamlit Cloud
- Implementado sistema multicapa de exportación a PDF con métodos alternativos
- Añadido método optimizado para Streamlit Cloud usando pdfkit y markdown2
- Implementada detección automática del entorno para seleccionar el mejor método de exportación

### Corregido
- Error "ModuleNotFoundError: No module named 'expert_selection'" al iniciar la aplicación

## [1.0.0] - 2025-04-29

### Añadido
- Versión inicial de Expert Nexus
- Sistema de múltiples expertos en una sola interfaz
- Gestión de expertos con selección manual
- Visualización del estado actual del experto
- Control de la conversación con selector manual y reinicio de sesión
- Procesamiento de documentos en formatos PDF, texto e imágenes
- Exportación de conversaciones en formato Markdown
