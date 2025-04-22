# Pruebas de Procesamiento de Documentos en Expert Nexus

Este directorio contiene scripts para probar, analizar y mejorar el procesamiento de documentos y el mantenimiento del contexto en Expert Nexus.

## Estructura de archivos

- `test_document_context.py`: Script principal de prueba que simula el flujo de carga de documentos y conversación con el asistente.
- `run_document_test.py`: Script para ejecutar las pruebas y analizar los resultados.
- `analyze_results.py`: Script para analizar los resultados de las pruebas y proponer soluciones.
- `implement_solutions.py`: Script para implementar las soluciones propuestas.
- `test_files/`: Directorio donde se guardan los archivos de prueba y los resultados.
- `backups/`: Directorio donde se guardan copias de seguridad de los archivos modificados.

## Requisitos previos

Antes de ejecutar las pruebas, asegúrate de tener configuradas las siguientes variables de entorno:

```bash
export OPENAI_API_KEY=tu_clave_api_openai
export MISTRAL_API_KEY=tu_clave_api_mistral
export ASSISTANT_ID=tu_id_asistente
```

## Cómo ejecutar las pruebas

1. **Ejecutar las pruebas**:

   ```bash
   cd test
   python run_document_test.py
   ```

   Este script creará archivos de prueba (PDF y texto), procesará los documentos y realizará una serie de intercambios con el asistente para verificar el mantenimiento del contexto.

2. **Analizar los resultados**:

   ```bash
   python analyze_results.py
   ```

   Este script analizará los resultados de la prueba más reciente y generará un informe con los problemas encontrados y las soluciones propuestas.

3. **Implementar las soluciones** (opcional):

   ```bash
   python implement_solutions.py
   ```

   Este script implementará automáticamente las soluciones propuestas, modificando el archivo `app.py`. Se creará una copia de seguridad del archivo original antes de realizar cualquier cambio.

## Interpretación de los resultados

Los resultados de las pruebas se guardan en el directorio `test_files/` con el formato `test_results_YYYYMMDD_HHMMSS.json`. El informe de soluciones se guarda como `solutions_report.md`.

### Problemas comunes y soluciones

1. **Procesamiento incorrecto de documentos**:
   - Verifica que PyPDF2 esté instalado correctamente.
   - Añade más manejo de errores en la extracción de texto.
   - Implementa métodos alternativos de extracción para diferentes tipos de PDF.

2. **Pérdida de contexto entre mensajes**:
   - Modifica la función `process_message` para incluir siempre el contenido de los documentos en cada mensaje.
   - Implementa un sistema de caché para documentos grandes.
   - Añade un sistema de referencias para que el asistente pueda citar los documentos.

3. **Problemas con documentos grandes**:
   - Implementa un sistema de resumen automático para documentos grandes.
   - Considera el uso de embeddings para documentos muy grandes en lugar de incluir el texto completo.

## Verificación manual

Después de implementar las soluciones, puedes verificar manualmente que los documentos se procesan correctamente y se mantienen en el contexto:

1. Ejecuta la aplicación Expert Nexus.
2. Carga un documento PDF o de texto.
3. Pregunta al asistente sobre el contenido del documento.
4. Continúa la conversación sin mencionar el documento y verifica si el asistente aún tiene acceso a su contenido.

## Notas adicionales

- Las pruebas están diseñadas para ser ejecutadas sin interfaz gráfica, lo que permite automatizar el proceso y recopilar resultados detallados.
- El script `implement_solutions.py` realiza modificaciones en el código fuente de la aplicación. Siempre se crea una copia de seguridad antes de realizar cambios.
- Si encuentras problemas después de implementar las soluciones, puedes restaurar la versión original del archivo `app.py` desde el directorio `backups/`.
