#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script completo para probar la funcionalidad de selección de expertos.
Este script prueba todos los escenarios posibles:
1. Seleccionar el experto sugerido
2. Continuar con el experto actual
3. No se detecta ningún experto sugerido
"""

import logging
import streamlit as st
from datetime import datetime
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_expert_selection")

# Configuración de expertos
assistants_config = {
    "tutela": {
        "id": "asst_xisQZwJ1bbmvXET8YG0eiAmb",
        "titulo": "TutelaBot - Asistente Especializado en Acción de Tutela y Derecho de Petición",
        "descripcion": "Experto en mecanismos constitucionales de protección de derechos"
    },
    "asistente_virtual": {
        "id": "asst_RfRNo5Ij76ieg7mV11CqYV9v",
        "titulo": "Asistente Virtual de Inteligencia Artificial",
        "descripcion": "Ayudante virtual con conocimiento amplio en múltiples disciplinas"
    },
    "transformacion_digital": {
        "id": "asst_abc123",
        "titulo": "Experto en Transformación Digital",
        "descripcion": "Especialista en procesos de transformación digital y tecnología"
    }
}

# Inicializar estado de sesión
if "current_expert" not in st.session_state:
    st.session_state.current_expert = "asistente_virtual"

if "assistants_config" not in st.session_state:
    st.session_state.assistants_config = assistants_config

if "expert_history" not in st.session_state:
    st.session_state.expert_history = []

if "expert_selection_state" not in st.session_state:
    st.session_state.expert_selection_state = {
        "pending": False,
        "message": "",
        "suggested_expert": "",
        "choice": None,
        "processed": False
    }

if "test_results" not in st.session_state:
    st.session_state.test_results = []

if "test_scenario" not in st.session_state:
    st.session_state.test_scenario = None

if "test_step" not in st.session_state:
    st.session_state.test_step = 0

# Función para procesar mensajes (simulación)
def process_message(message, expert_key):
    """Simula el procesamiento de un mensaje con un experto específico"""
    logger.info(f"Procesando mensaje con experto: {expert_key}")
    logger.info(f"Mensaje: '{message}'")
    
    # Simular respuesta según el experto
    if expert_key == "tutela":
        return "Como experto en tutelas, te informo que si han pasado más de 90 días sin respuesta a tu derecho de petición, puedes interponer una acción de tutela por violación al derecho fundamental de petición."
    elif expert_key == "transformacion_digital":
        return "Como experto en transformación digital, te recomiendo implementar soluciones tecnológicas para optimizar tus procesos."
    else:
        return f"Respuesta del experto {expert_key} a tu mensaje."

# Función para cambiar de experto
def change_expert(expert_key, reason="Selección manual"):
    """Cambia el experto actual y registra el cambio en el historial."""
    try:
        # Verificar que el experto exista
        if expert_key not in st.session_state.assistants_config:
            logger.warning(f"Experto '{expert_key}' no encontrado en la configuración")
            return False
        
        # Cambiar el experto actual
        st.session_state.current_expert = expert_key
        
        # Registrar el cambio en el historial
        st.session_state.expert_history.append({
            "timestamp": datetime.now().strftime("%I:%M:%S %p"),
            "expert": expert_key,
            "reason": reason
        })
        
        logger.info(f"Experto cambiado a '{expert_key}'. Razón: {reason}")
        return True
    except Exception as e:
        logger.error(f"Error al cambiar de experto: {str(e)}")
        return False

# Función para manejar la selección de expertos
def handle_expert_selection(user_text, suggested_expert):
    """Maneja el flujo de selección de expertos."""
    logger.info(f"handle_expert_selection - user_text: '{user_text[:50]}...', suggested_expert: '{suggested_expert}'")
    
    # Si no hay un experto sugerido o es el mismo que el actual, continuar con el flujo normal
    if not suggested_expert or suggested_expert == st.session_state.current_expert:
        logger.info("No hay experto sugerido o es el mismo que el actual, continuando con flujo normal")
        return True, None
    
    # Verificar que el experto sugerido exista
    if suggested_expert not in st.session_state.assistants_config:
        logger.warning(f"Experto sugerido '{suggested_expert}' no encontrado en la configuración")
        return True, None
    
    # Obtener el título del experto sugerido
    expert_titulo = st.session_state.assistants_config[suggested_expert]["titulo"]
    
    # Estado actual de la selección de expertos
    selection_state = st.session_state.expert_selection_state
    logger.info(f"Estado actual de selección: {selection_state}")
    
    # Si ya se procesó esta selección, continuar con el flujo normal
    if selection_state["processed"] and selection_state["message"] == user_text:
        logger.info("Esta selección ya fue procesada, continuando con flujo normal")
        # Reiniciar el estado para futuros mensajes
        selection_state["pending"] = False
        selection_state["message"] = ""
        selection_state["suggested_expert"] = ""
        selection_state["choice"] = None
        selection_state["processed"] = False
        logger.info("Estado de selección de expertos reiniciado")
        return True, None
    
    # Si hay una selección pendiente para este mensaje
    if selection_state["pending"] and selection_state["message"] == user_text:
        logger.info(f"Hay una selección pendiente para este mensaje. Choice: {selection_state['choice']}")
        # Si se ha hecho una elección
        if selection_state["choice"] is not None:
            try:
                if selection_state["choice"] == "suggested":
                    logger.info(f"Usuario eligió usar el experto sugerido: {selection_state['suggested_expert']}")
                    # Cambiar al experto sugerido
                    success = change_expert(selection_state["suggested_expert"], "Cambio automático por palabras clave")
                    logger.info(f"Cambio de experto result: {success}")
                    
                    if not success:
                        logger.error(f"No se pudo cambiar al experto sugerido: {selection_state['suggested_expert']}")
                        st.error(f"No se pudo cambiar al experto sugerido. Continuando con el experto actual.")
                        # Procesar con el experto actual como fallback
                        response_text = process_message(user_text, st.session_state.current_expert)
                    else:
                        # Procesar el mensaje con el experto sugerido
                        logger.info(f"Procesando mensaje con experto: {selection_state['suggested_expert']}")
                        response_text = process_message(user_text, selection_state["suggested_expert"])
                    
                    logger.info(f"Respuesta obtenida: {response_text is not None}")
                    
                    # Marcar como procesado
                    selection_state["processed"] = True
                    
                    # Devolver la respuesta
                    return False, response_text
                elif selection_state["choice"] == "current":
                    logger.info("Usuario eligió continuar con el experto actual")
                    # Procesar el mensaje con el experto actual
                    logger.info(f"Procesando mensaje con experto actual: {st.session_state.current_expert}")
                    response_text = process_message(user_text, st.session_state.current_expert)
                    logger.info(f"Respuesta obtenida: {response_text is not None}")
                    
                    # Marcar como procesado
                    selection_state["processed"] = True
                    
                    # Devolver la respuesta
                    return False, response_text
            except Exception as e:
                logger.error(f"Error al procesar la selección de experto: {str(e)}")
                st.error(f"Ocurrió un error al procesar tu mensaje. Por favor, inténtalo de nuevo.")
                # Reiniciar el estado para evitar bucles
                selection_state["pending"] = False
                selection_state["message"] = ""
                selection_state["suggested_expert"] = ""
                selection_state["choice"] = None
                selection_state["processed"] = False
                logger.info("Estado de selección de expertos reiniciado debido a un error")
                return True, None
    
    # Mostrar opciones de selección de experto
    logger.info(f"Mostrando opciones de selección para el experto: {suggested_expert}")
    st.info(f"Tu mensaje parece relacionado con '{expert_titulo}'. ¿Quieres cambiar de experto?")
    
    # Guardar información para la próxima ejecución
    selection_state["pending"] = True
    selection_state["message"] = user_text
    selection_state["suggested_expert"] = suggested_expert
    selection_state["choice"] = None
    selection_state["processed"] = False
    logger.info(f"Estado guardado para la próxima ejecución: {selection_state}")
    
    # Mostrar botones de selección
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Usar experto sugerido", key="use_suggested", use_container_width=True):
            logger.info(f"Botón 'Usar experto sugerido' presionado")
            selection_state["choice"] = "suggested"
            logger.info(f"Estado actualizado: {selection_state}")
            st.rerun()
    with col2:
        if st.button("Continuar con experto actual", key="keep_current", use_container_width=True):
            logger.info(f"Botón 'Continuar con experto actual' presionado")
            selection_state["choice"] = "current"
            logger.info(f"Estado actualizado: {selection_state}")
            st.rerun()
    
    # Detener el flujo normal
    logger.info("Deteniendo flujo normal para mostrar opciones de selección")
    return False, None

# Función para ejecutar un escenario de prueba
def run_test_scenario(scenario):
    st.session_state.test_scenario = scenario
    st.session_state.test_step = 1
    
    # Reiniciar el estado de selección de expertos
    st.session_state.expert_selection_state = {
        "pending": False,
        "message": "",
        "suggested_expert": "",
        "choice": None,
        "processed": False
    }
    
    # Reiniciar el historial de expertos
    st.session_state.expert_history = []
    
    # Establecer el experto actual según el escenario
    st.session_state.current_expert = "asistente_virtual"
    
    # Registrar el inicio de la prueba
    st.session_state.test_results.append({
        "timestamp": datetime.now().strftime("%I:%M:%S %p"),
        "scenario": scenario,
        "step": 1,
        "message": f"Iniciando prueba: {scenario}"
    })
    
    st.rerun()

# Función para verificar los resultados de la prueba
def verify_test_results(scenario):
    if scenario == "Seleccionar experto sugerido":
        # Verificar que el experto actual sea el sugerido (tutela)
        if st.session_state.current_expert == "tutela":
            return True, "Prueba exitosa: Se cambió al experto sugerido correctamente"
        else:
            return False, f"Prueba fallida: No se cambió al experto sugerido. Experto actual: {st.session_state.current_expert}"
    
    elif scenario == "Continuar con experto actual":
        # Verificar que el experto actual siga siendo el mismo (asistente_virtual)
        if st.session_state.current_expert == "asistente_virtual":
            return True, "Prueba exitosa: Se continuó con el experto actual correctamente"
        else:
            return False, f"Prueba fallida: Se cambió el experto. Experto actual: {st.session_state.current_expert}"
    
    elif scenario == "Sin experto sugerido":
        # Verificar que el experto actual siga siendo el mismo (asistente_virtual)
        if st.session_state.current_expert == "asistente_virtual":
            return True, "Prueba exitosa: Se procesó el mensaje con el experto actual correctamente"
        else:
            return False, f"Prueba fallida: Se cambió el experto. Experto actual: {st.session_state.current_expert}"
    
    return False, "Escenario de prueba desconocido"

# Función principal
def main():
    st.title("Prueba Completa de Selección de Expertos")
    
    # Mostrar información del experto actual
    st.subheader("Experto Actual")
    current_expert_key = st.session_state.current_expert
    current_expert = st.session_state.assistants_config[current_expert_key]
    st.write(f"**{current_expert['titulo']}**")
    st.write(current_expert['descripcion'])
    
    # Mostrar historial de expertos
    if st.session_state.expert_history:
        st.subheader("Historial de Expertos")
        for entry in st.session_state.expert_history:
            expert_key = entry["expert"]
            expert_title = st.session_state.assistants_config[expert_key]["titulo"]
            st.write(f"**{entry['timestamp']}**: {expert_title} - {entry['reason']}")
    
    # Sección de pruebas
    st.subheader("Pruebas de Selección de Expertos")
    
    # Botones para iniciar las pruebas
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Prueba 1: Seleccionar experto sugerido", use_container_width=True):
            run_test_scenario("Seleccionar experto sugerido")
    with col2:
        if st.button("Prueba 2: Continuar con experto actual", use_container_width=True):
            run_test_scenario("Continuar con experto actual")
    with col3:
        if st.button("Prueba 3: Sin experto sugerido", use_container_width=True):
            run_test_scenario("Sin experto sugerido")
    
    # Ejecutar el escenario de prueba actual
    if st.session_state.test_scenario:
        st.subheader(f"Ejecutando prueba: {st.session_state.test_scenario}")
        
        # Paso 1: Enviar mensaje
        if st.session_state.test_step == 1:
            st.info("Paso 1: Enviando mensaje de prueba...")
            
            # Definir mensaje y experto sugerido según el escenario
            if st.session_state.test_scenario == "Seleccionar experto sugerido":
                user_text = "Envie un derecho de petición y no he recibido respuesta aun despues de mas de 90 días. Que puedo hacer?"
                suggested_expert = "tutela"
            elif st.session_state.test_scenario == "Continuar con experto actual":
                user_text = "Envie un derecho de petición y no he recibido respuesta aun despues de mas de 90 días. Que puedo hacer?"
                suggested_expert = "tutela"
            else:  # Sin experto sugerido
                user_text = "¿Cuál es la capital de Francia?"
                suggested_expert = None
            
            # Registrar el mensaje
            st.session_state.test_results.append({
                "timestamp": datetime.now().strftime("%I:%M:%S %p"),
                "scenario": st.session_state.test_scenario,
                "step": 1,
                "message": f"Mensaje: '{user_text}', Experto sugerido: '{suggested_expert}'"
            })
            
            # Manejar la selección de expertos
            continue_normal_flow, response_text = handle_expert_selection(user_text, suggested_expert)
            
            # Registrar el resultado
            st.session_state.test_results.append({
                "timestamp": datetime.now().strftime("%I:%M:%S %p"),
                "scenario": st.session_state.test_scenario,
                "step": 1,
                "message": f"Resultado: continue_normal_flow={continue_normal_flow}, response_text={response_text is not None}"
            })
            
            # Si no hay experto sugerido o es el mismo que el actual, procesar directamente
            if st.session_state.test_scenario == "Sin experto sugerido" or continue_normal_flow:
                response_text = process_message(user_text, st.session_state.current_expert)
                st.success(response_text)
                
                # Verificar los resultados
                success, message = verify_test_results(st.session_state.test_scenario)
                
                # Registrar el resultado
                st.session_state.test_results.append({
                    "timestamp": datetime.now().strftime("%I:%M:%S %p"),
                    "scenario": st.session_state.test_scenario,
                    "step": "final",
                    "message": message
                })
                
                if success:
                    st.success(message)
                else:
                    st.error(message)
                
                # Finalizar la prueba
                st.session_state.test_step = 0
                st.session_state.test_scenario = None
            else:
                # Pasar al paso 2
                st.session_state.test_step = 2
                st.rerun()
        
        # Paso 2: Seleccionar opción
        elif st.session_state.test_step == 2:
            st.info("Paso 2: Seleccionando opción...")
            
            # Simular la selección según el escenario
            if st.session_state.test_scenario == "Seleccionar experto sugerido":
                # Simular clic en "Usar experto sugerido"
                st.session_state.expert_selection_state["choice"] = "suggested"
            else:  # Continuar con experto actual
                # Simular clic en "Continuar con experto actual"
                st.session_state.expert_selection_state["choice"] = "current"
            
            # Registrar la selección
            st.session_state.test_results.append({
                "timestamp": datetime.now().strftime("%I:%M:%S %p"),
                "scenario": st.session_state.test_scenario,
                "step": 2,
                "message": f"Selección: {st.session_state.expert_selection_state['choice']}"
            })
            
            # Pasar al paso 3
            st.session_state.test_step = 3
            time.sleep(1)  # Pequeña pausa para simular el tiempo de procesamiento
            st.rerun()
        
        # Paso 3: Procesar respuesta
        elif st.session_state.test_step == 3:
            st.info("Paso 3: Procesando respuesta...")
            
            # Definir mensaje según el escenario
            if st.session_state.test_scenario == "Seleccionar experto sugerido" or st.session_state.test_scenario == "Continuar con experto actual":
                user_text = "Envie un derecho de petición y no he recibido respuesta aun despues de mas de 90 días. Que puedo hacer?"
                suggested_expert = "tutela"
            else:  # Sin experto sugerido
                user_text = "¿Cuál es la capital de Francia?"
                suggested_expert = None
            
            # Manejar la selección de expertos
            continue_normal_flow, response_text = handle_expert_selection(user_text, suggested_expert)
            
            # Registrar el resultado
            st.session_state.test_results.append({
                "timestamp": datetime.now().strftime("%I:%M:%S %p"),
                "scenario": st.session_state.test_scenario,
                "step": 3,
                "message": f"Resultado: continue_normal_flow={continue_normal_flow}, response_text={response_text is not None}"
            })
            
            # Mostrar la respuesta
            if response_text:
                st.success(response_text)
            
            # Verificar los resultados
            success, message = verify_test_results(st.session_state.test_scenario)
            
            # Registrar el resultado
            st.session_state.test_results.append({
                "timestamp": datetime.now().strftime("%I:%M:%S %p"),
                "scenario": st.session_state.test_scenario,
                "step": "final",
                "message": message
            })
            
            if success:
                st.success(message)
            else:
                st.error(message)
            
            # Finalizar la prueba
            st.session_state.test_step = 0
            st.session_state.test_scenario = None
    
    # Mostrar resultados de las pruebas
    if st.session_state.test_results:
        st.subheader("Resultados de las Pruebas")
        for result in st.session_state.test_results:
            st.write(f"**{result['timestamp']}** - Escenario: {result['scenario']}, Paso: {result['step']}")
            st.write(f"  {result['message']}")
        
        if st.button("Limpiar resultados"):
            st.session_state.test_results = []
            st.rerun()

if __name__ == "__main__":
    main()
