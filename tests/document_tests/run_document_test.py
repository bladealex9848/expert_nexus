"""
Script para ejecutar la prueba de procesamiento de documentos y análisis de resultados.
"""

import os
import sys
import json
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - RUN_TEST - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Directorio actual
current_dir = os.path.dirname(os.path.abspath(__file__))

# Verificar variables de entorno necesarias
required_env_vars = ["OPENAI_API_KEY", "MISTRAL_API_KEY", "ASSISTANT_ID"]
missing_vars = [var for var in required_env_vars if not os.environ.get(var)]

if missing_vars:
    logging.error(f"Faltan variables de entorno: {', '.join(missing_vars)}")
    logging.info("Por favor, configura las variables de entorno antes de ejecutar la prueba:")
    for var in missing_vars:
        logging.info(f"  export {var}=tu_valor")
    sys.exit(1)

# Crear directorio para archivos de prueba
test_files_dir = os.path.join(current_dir, "test_files")
os.makedirs(test_files_dir, exist_ok=True)

# Ejecutar prueba
try:
    logging.info("Ejecutando prueba de procesamiento de documentos...")
    from test_document_context import run_test
    
    # Ejecutar prueba y obtener resultados
    test_results = run_test()
    
    # Guardar resultados con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_path = os.path.join(test_files_dir, f"test_results_{timestamp}.json")
    
    with open(results_path, "w") as f:
        json.dump(test_results, f, indent=2)
    
    logging.info(f"Resultados guardados en: {results_path}")
    
    # Analizar resultados
    logging.info("\n" + "="*50)
    logging.info("ANÁLISIS DE RESULTADOS")
    logging.info("="*50)
    
    # Verificar éxito general
    if test_results["success"]:
        logging.info("✅ Prueba completada con éxito")
    else:
        logging.error("❌ Prueba fallida")
        for error in test_results["errors"]:
            logging.error(f"  - {error}")
    
    # Analizar procesamiento de documentos
    logging.info("\nPROCESAMIENTO DE DOCUMENTOS:")
    for doc_type, result in test_results["document_processing"].items():
        if result["success"]:
            logging.info(f"✅ {doc_type.upper()}: Procesado correctamente ({result['text_length']} caracteres, formato: {result.get('format', 'desconocido')})")
        else:
            logging.error(f"❌ {doc_type.upper()}: Error en procesamiento")
    
    # Analizar conversación
    logging.info("\nANÁLISIS DE CONVERSACIÓN:")
    
    # Definir palabras clave para verificar si el asistente reconoce los documentos
    document_keywords = [
        "documento", "pdf", "texto", "archivo", 
        "test_document.pdf", "test_document.txt",
        "código secreto", "12345", "versión", "1.0.0"
    ]
    
    for i, exchange in enumerate(test_results["conversation"]):
        logging.info(f"\nIntercambio {i+1}:")
        logging.info(f"  Pregunta: {exchange['user']}")
        
        # Verificar si hay respuesta
        if not exchange["assistant"]:
            logging.error(f"  ❌ No se recibió respuesta del asistente")
            continue
            
        # Mostrar fragmento de la respuesta
        response_preview = exchange["assistant"][:150] + "..." if len(exchange["assistant"]) > 150 else exchange["assistant"]
        logging.info(f"  Respuesta: {response_preview}")
        
        # Verificar si la respuesta menciona los documentos
        keywords_found = [kw for kw in document_keywords if kw.lower() in exchange["assistant"].lower()]
        
        # Analizar si el asistente reconoce los documentos
        docs_in_context = len(exchange["documents_in_context"]) > 0
        if docs_in_context and keywords_found:
            logging.info(f"  ✅ El asistente reconoce los documentos (palabras clave encontradas: {', '.join(keywords_found[:3])})")
        elif docs_in_context and not keywords_found:
            logging.warning(f"  ⚠️ Documentos incluidos pero el asistente no parece reconocerlos")
        elif not docs_in_context and keywords_found:
            logging.info(f"  ✅ El asistente mantiene el contexto de documentos previos")
        else:
            logging.warning(f"  ⚠️ No hay documentos en contexto ni menciones a ellos")
    
    # Conclusiones
    logging.info("\n" + "="*50)
    logging.info("CONCLUSIONES")
    logging.info("="*50)
    
    # Verificar si el procesamiento de documentos funciona
    doc_processing_success = all(result["success"] for result in test_results["document_processing"].values())
    if doc_processing_success:
        logging.info("✅ El procesamiento de documentos funciona correctamente")
    else:
        logging.error("❌ Hay problemas en el procesamiento de documentos")
    
    # Verificar si el contexto se mantiene
    context_maintained = False
    if len(test_results["conversation"]) >= 4:
        # Verificar si en la prueba 4 (sin documentos) el asistente aún recuerda información
        fourth_exchange = test_results["conversation"][3]
        if any(kw.lower() in fourth_exchange["assistant"].lower() for kw in document_keywords):
            context_maintained = True
    
    if context_maintained:
        logging.info("✅ El contexto de los documentos se mantiene entre mensajes")
    else:
        logging.warning("⚠️ El contexto de los documentos podría no mantenerse correctamente")
    
    # Recomendaciones
    logging.info("\nRECOMENDACIONES:")
    
    if not doc_processing_success:
        logging.info("- Revisar el procesamiento de documentos para asegurar que se extraiga correctamente el texto")
    
    if not context_maintained:
        logging.info("- Modificar la función process_message para incluir siempre el contenido de los documentos en cada mensaje")
        logging.info("- Verificar que st.session_state.document_contents se mantiene correctamente entre interacciones")
    
    logging.info("- Realizar pruebas adicionales con diferentes tipos y tamaños de documentos")
    
except Exception as e:
    logging.error(f"Error ejecutando la prueba: {str(e)}")
    import traceback
    logging.error(traceback.format_exc())
