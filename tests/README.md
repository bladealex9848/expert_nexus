# Pruebas de Expert Nexus

Este directorio contiene los scripts de prueba para verificar el correcto funcionamiento de Expert Nexus.

## Estructura de pruebas

### Pruebas de selección de expertos

- `test_expert_selection.py`: Prueba básica de la funcionalidad de selección de expertos.
- `test_expert_selection_simple.py`: Versión simplificada de las pruebas de selección de expertos.
- `test_expert_selection_scenarios.py`: Pruebas de escenarios específicos de selección de expertos.
- `test_expert_selection_automated.py`: Pruebas automatizadas de selección de expertos.
- `test_expert_selection_complete.py`: Pruebas completas de selección de expertos.
- `test_expert_flow.py`: Pruebas del flujo de cambio de expertos.

### Pruebas de integración

- `test_app_integration.py`: Pruebas de integración con la aplicación principal.

### Pruebas de procesamiento de documentos

Ubicadas en el subdirectorio `document_tests/`:

- `test_document_context.py`: Prueba principal del procesamiento de documentos y mantenimiento del contexto.
- `run_document_test.py`: Script para ejecutar las pruebas de documentos.
- `analyze_results.py`: Script para analizar los resultados de las pruebas.
- `implement_solutions.py`: Script para implementar soluciones a problemas detectados.
- `run_all.py`: Script para ejecutar todas las pruebas de documentos.
- `setup.py`: Script para configurar el entorno de pruebas.
- `set_env.py`: Script para configurar variables de entorno.

## Cómo ejecutar las pruebas

### Pruebas de selección de expertos

```bash
python tests/test_expert_selection.py
```

### Pruebas de integración

```bash
python tests/test_app_integration.py
```

### Pruebas de procesamiento de documentos

```bash
cd tests/document_tests
python run_all.py
```

## Requisitos previos

Antes de ejecutar las pruebas, asegúrate de tener configuradas las siguientes variables de entorno:

```bash
export OPENAI_API_KEY=tu_clave_api_openai
export MISTRAL_API_KEY=tu_clave_api_mistral
export ASSISTANT_ID=tu_id_asistente
```

## Interpretación de los resultados

Los resultados de las pruebas de documentos se guardan en el directorio `document_tests/test_files/` con el formato `test_results_YYYYMMDD_HHMMSS.json`. El informe de soluciones se guarda como `solutions_report.md`.
