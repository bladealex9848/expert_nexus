"""
Script para analizar los resultados de las pruebas de procesamiento de documentos
y proponer soluciones a los problemas encontrados.
"""

import os
import sys
import json
import glob
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - ANALYSIS - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Directorio actual
current_dir = os.path.dirname(os.path.abspath(__file__))
test_files_dir = os.path.join(current_dir, "test_files")

# Función para encontrar el archivo de resultados más reciente
def find_latest_results():
    result_files = glob.glob(os.path.join(test_files_dir, "test_results_*.json"))
    if not result_files:
        return None
    
    # Ordenar por fecha de modificación (más reciente primero)
    result_files.sort(key=os.path.getmtime, reverse=True)
    return result_files[0]

# Función para analizar resultados y proponer soluciones
def analyze_results(results_file):
    try:
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        logging.info(f"Analizando resultados de: {os.path.basename(results_file)}")
        
        # Problemas identificados
        problems = []
        
        # Verificar procesamiento de documentos
        for doc_type, result in results["document_processing"].items():
            if not result["success"]:
                problems.append(f"Error procesando documento {doc_type}")
        
        # Verificar si el asistente reconoce los documentos
        document_keywords = [
            "documento", "pdf", "texto", "archivo", 
            "test_document.pdf", "test_document.txt",
            "código secreto", "12345", "versión", "1.0.0"
        ]
        
        context_issues = []
        
        for i, exchange in enumerate(results["conversation"]):
            # Verificar si hay respuesta
            if not exchange["assistant"]:
                problems.append(f"No se recibió respuesta del asistente en el intercambio {i+1}")
                continue
                
            # Verificar si la respuesta menciona los documentos cuando deberían estar en contexto
            keywords_found = [kw for kw in document_keywords if kw.lower() in exchange["assistant"].lower()]
            docs_in_context = len(exchange["documents_in_context"]) > 0
            
            if docs_in_context and not keywords_found:
                context_issues.append(f"Intercambio {i+1}: Documentos incluidos pero no reconocidos")
            elif not docs_in_context and not keywords_found and i > 0:
                context_issues.append(f"Intercambio {i+1}: Contexto de documentos perdido")
        
        if context_issues:
            problems.append("Problemas de contexto de documentos: " + "; ".join(context_issues))
        
        # Generar informe
        logging.info("\n" + "="*50)
        logging.info("INFORME DE ANÁLISIS")
        logging.info("="*50)
        
        if not problems:
            logging.info("✅ No se encontraron problemas significativos")
        else:
            logging.warning(f"⚠️ Se encontraron {len(problems)} problemas:")
            for i, problem in enumerate(problems):
                logging.warning(f"  {i+1}. {problem}")
        
        # Proponer soluciones
        logging.info("\n" + "="*50)
        logging.info("SOLUCIONES PROPUESTAS")
        logging.info("="*50)
        
        if not problems:
            logging.info("No se requieren cambios inmediatos.")
        else:
            # Soluciones específicas según los problemas encontrados
            if any("Error procesando documento" in p for p in problems):
                logging.info("1. Mejorar el procesamiento de documentos:")
                logging.info("   - Verificar que PyPDF2 está instalado correctamente")
                logging.info("   - Añadir más manejo de errores en la extracción de texto")
                logging.info("   - Implementar métodos alternativos de extracción para diferentes tipos de PDF")
            
            if any("Problemas de contexto" in p for p in problems):
                logging.info("2. Solucionar problemas de contexto:")
                logging.info("   - Modificar la función process_message para incluir SIEMPRE el contenido de los documentos en cada mensaje")
                logging.info("   - Implementar un sistema de caché para documentos grandes")
                logging.info("   - Añadir un sistema de referencias para que el asistente pueda citar los documentos")
                
                # Proponer cambio específico en el código
                logging.info("\nCambio propuesto en app.py (función process_message):")
                logging.info("""
@handle_error(max_retries=1)
def process_message(message, expert_key):
    # Obtener el ID del asistente del expert_key
    assistant_id = st.session_state.assistants_config[expert_key]["id"]
    
    # Enriquecer el mensaje con el contenido de los documentos
    full_message = message
    
    # SIEMPRE verificar si hay documentos en la sesión
    if "document_contents" in st.session_state and st.session_state.document_contents:
        document_context = "\\n\\n### Contenido de documentos adjuntos:\\n\\n"
        
        for doc_name, doc_content in st.session_state.document_contents.items():
            # Extraer el texto del documento
            if isinstance(doc_content, dict) and "text" in doc_content:
                # Limitar el contenido para no exceder el contexto
                doc_text = doc_content["text"][:10000] + "..." if len(doc_content["text"]) > 10000 else doc_content["text"]
                document_context += f"-- Documento: {doc_name} --\\n{doc_text}\\n\\n"
            elif isinstance(doc_content, dict) and "error" in doc_content:
                document_context += f"-- Documento: {doc_name} -- (Error: {doc_content.get('error', 'Error desconocido')})\\n\\n"
        
        # Añadir el contexto de documentos al mensaje si hay contenido real
        if len(document_context) > 60:  # Más que solo el encabezado
            full_message = f"{message}\\n\\n{document_context}"
            logging.info(f"Mensaje enriquecido con {len(st.session_state.document_contents)} documentos. Tamaño total: {len(full_message)} caracteres")
    
    # Añadir el mensaje a la conversación
    st.session_state.client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=full_message
    )
                """)
            
            logging.info("\n3. Mejoras adicionales:")
            logging.info("   - Implementar un sistema de verificación que confirme que el asistente ha recibido los documentos")
            logging.info("   - Añadir un indicador visual en la interfaz que muestre qué documentos están activos en el contexto")
            logging.info("   - Crear un sistema de resumen automático para documentos grandes")
        
        # Recomendaciones generales
        logging.info("\nRecomendaciones generales:")
        logging.info("1. Realizar pruebas con documentos más grandes y complejos")
        logging.info("2. Implementar un sistema de logging más detallado para el procesamiento de documentos")
        logging.info("3. Considerar el uso de embeddings para documentos muy grandes en lugar de incluir el texto completo")
        
        # Conclusión
        logging.info("\nConclusión:")
        if len(problems) > 3:
            logging.warning("Se requieren cambios significativos para mejorar el manejo de documentos.")
        elif len(problems) > 0:
            logging.info("Con algunos ajustes menores, el sistema debería funcionar correctamente.")
        else:
            logging.info("El sistema está funcionando correctamente, solo se recomiendan mejoras incrementales.")
    
    return problems
        
    except Exception as e:
        logging.error(f"Error analizando resultados: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return ["Error en el análisis: " + str(e)]

# Función principal
def main():
    # Encontrar el archivo de resultados más reciente
    results_file = find_latest_results()
    
    if not results_file:
        logging.error("No se encontraron archivos de resultados. Ejecuta primero run_document_test.py")
        return
    
    # Analizar resultados
    problems = analyze_results(results_file)
    
    # Generar informe de soluciones
    solutions_file = os.path.join(test_files_dir, "solutions_report.md")
    
    with open(solutions_file, "w") as f:
        f.write("# Informe de Soluciones para Expert Nexus\n\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Basado en: {os.path.basename(results_file)}\n\n")
        
        f.write("## Problemas Identificados\n\n")
        
        if not problems:
            f.write("No se encontraron problemas significativos.\n\n")
        else:
            for i, problem in enumerate(problems):
                f.write(f"{i+1}. {problem}\n")
            f.write("\n")
        
        f.write("## Soluciones Propuestas\n\n")
        
        if not problems:
            f.write("No se requieren cambios inmediatos.\n\n")
        else:
            # Soluciones específicas según los problemas encontrados
            if any("Error procesando documento" in p for p in problems):
                f.write("### 1. Mejorar el procesamiento de documentos\n\n")
                f.write("- Verificar que PyPDF2 está instalado correctamente\n")
                f.write("- Añadir más manejo de errores en la extracción de texto\n")
                f.write("- Implementar métodos alternativos de extracción para diferentes tipos de PDF\n\n")
            
            if any("Problemas de contexto" in p for p in problems):
                f.write("### 2. Solucionar problemas de contexto\n\n")
                f.write("- Modificar la función process_message para incluir SIEMPRE el contenido de los documentos en cada mensaje\n")
                f.write("- Implementar un sistema de caché para documentos grandes\n")
                f.write("- Añadir un sistema de referencias para que el asistente pueda citar los documentos\n\n")
                
                # Proponer cambio específico en el código
                f.write("#### Cambio propuesto en app.py (función process_message):\n\n")
                f.write("```python\n")
                f.write("""@handle_error(max_retries=1)
def process_message(message, expert_key):
    # Obtener el ID del asistente del expert_key
    assistant_id = st.session_state.assistants_config[expert_key]["id"]
    
    # Enriquecer el mensaje con el contenido de los documentos
    full_message = message
    
    # SIEMPRE verificar si hay documentos en la sesión
    if "document_contents" in st.session_state and st.session_state.document_contents:
        document_context = "\\n\\n### Contenido de documentos adjuntos:\\n\\n"
        
        for doc_name, doc_content in st.session_state.document_contents.items():
            # Extraer el texto del documento
            if isinstance(doc_content, dict) and "text" in doc_content:
                # Limitar el contenido para no exceder el contexto
                doc_text = doc_content["text"][:10000] + "..." if len(doc_content["text"]) > 10000 else doc_content["text"]
                document_context += f"-- Documento: {doc_name} --\\n{doc_text}\\n\\n"
            elif isinstance(doc_content, dict) and "error" in doc_content:
                document_context += f"-- Documento: {doc_name} -- (Error: {doc_content.get('error', 'Error desconocido')})\\n\\n"
        
        # Añadir el contexto de documentos al mensaje si hay contenido real
        if len(document_context) > 60:  # Más que solo el encabezado
            full_message = f"{message}\\n\\n{document_context}"
            logging.info(f"Mensaje enriquecido con {len(st.session_state.document_contents)} documentos. Tamaño total: {len(full_message)} caracteres")
    
    # Añadir el mensaje a la conversación
    st.session_state.client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=full_message
    )
""")
                f.write("```\n\n")
            
            f.write("### 3. Mejoras adicionales\n\n")
            f.write("- Implementar un sistema de verificación que confirme que el asistente ha recibido los documentos\n")
            f.write("- Añadir un indicador visual en la interfaz que muestre qué documentos están activos en el contexto\n")
            f.write("- Crear un sistema de resumen automático para documentos grandes\n\n")
        
        # Recomendaciones generales
        f.write("## Recomendaciones Generales\n\n")
        f.write("1. Realizar pruebas con documentos más grandes y complejos\n")
        f.write("2. Implementar un sistema de logging más detallado para el procesamiento de documentos\n")
        f.write("3. Considerar el uso de embeddings para documentos muy grandes en lugar de incluir el texto completo\n\n")
        
        # Conclusión
        f.write("## Conclusión\n\n")
        if len(problems) > 3:
            f.write("Se requieren cambios significativos para mejorar el manejo de documentos.\n")
        elif len(problems) > 0:
            f.write("Con algunos ajustes menores, el sistema debería funcionar correctamente.\n")
        else:
            f.write("El sistema está funcionando correctamente, solo se recomiendan mejoras incrementales.\n")
    
    logging.info(f"Informe de soluciones guardado en: {solutions_file}")

if __name__ == "__main__":
    main()
