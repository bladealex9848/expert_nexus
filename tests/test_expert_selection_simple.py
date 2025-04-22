#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script simple para probar la funcionalidad de selección de expertos.
"""

import logging
import streamlit as st
from datetime import datetime

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

# Función para procesar mensajes (simulación)
def process_message(message, expert_key):
    """Simula el procesamiento de un mensaje con un experto específico"""
    logger.info(f"Procesando mensaje con experto: {expert_key}")
    logger.info(f"Mensaje: '{message}'")
    
    # Simular respuesta según el experto
    if expert_key == "tutela":
        return "Como experto en tutelas, te informo que si han pasado más de 90 días sin respuesta a tu derecho de petición, puedes interponer una acción de tutela por violación al derecho fundamental de petición."
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
        return True, None
    
    # Si hay una selección pendiente para este mensaje
    if selection_state["pending"] and selection_state["message"] == user_text:
        logger.info(f"Hay una selección pendiente para este mensaje. Choice: {selection_state['choice']}")
        # Si se ha hecho una elección
        if selection_state["choice"] is not None:
            if selection_state["choice"] == "suggested":
                logger.info(f"Usuario eligió usar el experto sugerido: {selection_state['suggested_expert']}")
                # Cambiar al experto sugerido
                success = change_expert(selection_state["suggested_expert"], "Cambio automático por palabras clave")
                logger.info(f"Cambio de experto result: {success}")
                
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

# Función principal
def main():
    st.title("Prueba de Selección de Expertos")
    
    # Mostrar información del experto actual
    st.subheader("Experto Actual")
    current_expert_key = st.session_state.current_expert
    current_expert = st.session_state.assistants_config[current_expert_key]
    st.write(f"**{current_expert['titulo']}**")
    st.write(current_expert['descripcion'])
    
    # Mostrar historial de expertos
    st.subheader("Historial de Expertos")
    for entry in st.session_state.expert_history:
        expert_key = entry["expert"]
        expert_title = st.session_state.assistants_config[expert_key]["titulo"]
        st.write(f"**{entry['timestamp']}**: {expert_title} - {entry['reason']}")
    
    # Entrada de usuario
    user_text = st.text_input("Escribe tu mensaje:", "Envie un derecho de petición y no he recibido respuesta aun despues de mas de 90 días. Que puedo hacer?")
    
    # Detectar experto sugerido
    suggested_expert = "tutela" if "derecho de petición" in user_text.lower() or "tutela" in user_text.lower() else None
    
    # Botón para enviar mensaje
    if st.button("Enviar"):
        # Manejar la selección de expertos
        continue_normal_flow, response_text = handle_expert_selection(user_text, suggested_expert)
        
        # Si no debemos continuar con el flujo normal, significa que se está manejando la selección de expertos
        if not continue_normal_flow:
            # Si hay una respuesta, significa que se procesó el mensaje con un experto
            if response_text:
                st.success(response_text)
            # Si no hay respuesta, significa que se están mostrando las opciones de selección
            st.stop()
        
        # Si llegamos aquí, continuamos con el flujo normal (procesar con el experto actual)
        response_text = process_message(user_text, st.session_state.current_expert)
        st.success(response_text)

if __name__ == "__main__":
    main()
