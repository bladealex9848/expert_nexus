#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para manejar la selección de expertos en Expert Nexus.
Este módulo contiene funciones para detectar y cambiar expertos,
así como para manejar el flujo de selección de expertos.
"""

import streamlit as st
import logging
from datetime import datetime

def initialize_expert_selection_state():
    """
    Inicializa las variables de estado necesarias para la selección de expertos.
    """
    if "expert_selection_state" not in st.session_state:
        st.session_state.expert_selection_state = {
            "pending": False,
            "message": "",
            "suggested_expert": "",
            "choice": None,
            "processed": False
        }

def reset_expert_selection_state():
    """
    Reinicia el estado de selección de expertos.
    """
    st.session_state.expert_selection_state = {
        "pending": False,
        "message": "",
        "suggested_expert": "",
        "choice": None,
        "processed": False
    }

def detect_expert(message, keywords_dict):
    """
    Analiza el texto del mensaje y sugiere el experto más adecuado
    basado en palabras clave.

    Parámetros:
        message: Texto del mensaje del usuario
        keywords_dict: Diccionario de palabras clave por experto

    Retorno:
        string: Clave del experto sugerido o None si no hay coincidencias
    """
    if not message:
        return None

    message_lower = message.lower()
    matches = {}

    # Buscar coincidencias de palabras clave
    for expert, keywords in keywords_dict.items():
        # Verificar que el experto exista en la configuración actual
        if expert in st.session_state.assistants_config:
            match_count = sum(1 for keyword in keywords if keyword in message_lower)
            if match_count > 0:
                matches[expert] = match_count

    # Si encontramos coincidencias con palabras clave, usamos esa detección
    if matches:
        suggested_expert = max(matches.items(), key=lambda x: x[1])[0]
        logging.info(f"Experto sugerido por palabras clave: {suggested_expert}")
        return suggested_expert
    
    return None

def change_expert(expert_key, reason="Selección manual"):
    """
    Cambia el experto actual y registra el cambio en el historial.

    Parámetros:
        expert_key: Clave del experto al que se cambiará
        reason: Razón del cambio de experto

    Retorno:
        bool: True si el cambio fue exitoso, False en caso contrario
    """
    try:
        # Verificar que el experto exista
        if expert_key not in st.session_state.assistants_config:
            logging.warning(f"Experto '{expert_key}' no encontrado en la configuración")
            return False
        
        # Cambiar el experto actual
        st.session_state.current_expert = expert_key
        
        # Registrar el cambio en el historial
        st.session_state.expert_history.append({
            "timestamp": datetime.now().strftime("%I:%M:%S %p"),
            "expert": expert_key,
            "reason": reason
        })
        
        logging.info(f"Experto cambiado a '{expert_key}'. Razón: {reason}")
        return True
    except Exception as e:
        logging.error(f"Error al cambiar de experto: {str(e)}")
        return False

def handle_expert_selection(user_text, suggested_expert, process_message_func):
    """
    Maneja el flujo de selección de expertos.

    Parámetros:
        user_text: Texto del mensaje del usuario
        suggested_expert: Experto sugerido para el mensaje
        process_message_func: Función para procesar el mensaje con un experto

    Retorno:
        tuple: (bool, str) - (Continuar con el flujo normal, Texto de respuesta)
    """
    # Inicializar el estado de selección de expertos si no existe
    initialize_expert_selection_state()
    
    # Si no hay un experto sugerido o es el mismo que el actual, continuar con el flujo normal
    if not suggested_expert or suggested_expert == st.session_state.current_expert:
        return True, None
    
    # Verificar que el experto sugerido exista
    if suggested_expert not in st.session_state.assistants_config:
        logging.warning(f"Experto sugerido '{suggested_expert}' no encontrado en la configuración")
        return True, None
    
    # Obtener el título del experto sugerido
    expert_titulo = st.session_state.assistants_config[suggested_expert]["titulo"]
    
    # Estado actual de la selección de expertos
    selection_state = st.session_state.expert_selection_state
    
    # Si ya se procesó esta selección, continuar con el flujo normal
    if selection_state["processed"] and selection_state["message"] == user_text:
        return True, None
    
    # Si hay una selección pendiente para este mensaje
    if selection_state["pending"] and selection_state["message"] == user_text:
        # Si se ha hecho una elección
        if selection_state["choice"] is not None:
            if selection_state["choice"] == "suggested":
                # Usar el experto sugerido
                with st.spinner(f"Procesando tu mensaje con {st.session_state.assistants_config[selection_state['suggested_expert']]['titulo']}..."):
                    # Cambiar al experto sugerido
                    change_expert(selection_state["suggested_expert"], "Cambio automático por palabras clave")
                    
                    # Procesar el mensaje con el experto sugerido
                    response_text = process_message_func(user_text, selection_state["suggested_expert"])
                    
                    # Marcar como procesado
                    selection_state["processed"] = True
                    
                    # Devolver la respuesta
                    return False, response_text
            elif selection_state["choice"] == "current":
                # Continuar con el experto actual
                with st.spinner(f"Procesando tu mensaje con {st.session_state.assistants_config[st.session_state.current_expert]['titulo']}..."):
                    # Procesar el mensaje con el experto actual
                    response_text = process_message_func(user_text, st.session_state.current_expert)
                    
                    # Marcar como procesado
                    selection_state["processed"] = True
                    
                    # Devolver la respuesta
                    return False, response_text
    else:
        # Mostrar opciones de selección de experto
        st.info(f"Tu mensaje parece relacionado con '{expert_titulo}'. ¿Quieres cambiar de experto?")
        
        # Guardar información para la próxima ejecución
        selection_state["pending"] = True
        selection_state["message"] = user_text
        selection_state["suggested_expert"] = suggested_expert
        selection_state["choice"] = None
        selection_state["processed"] = False
        
        # Mostrar botones de selección
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Usar experto sugerido", key="use_suggested", use_container_width=True):
                selection_state["choice"] = "suggested"
                st.rerun()
        with col2:
            if st.button("Continuar con experto actual", key="keep_current", use_container_width=True):
                selection_state["choice"] = "current"
                st.rerun()
        
        # Detener el flujo normal
        return False, None
    
    # Por defecto, continuar con el flujo normal
    return True, None

def reset_for_new_message():
    """
    Reinicia el estado de selección de expertos para un nuevo mensaje.
    """
    # Si el mensaje actual ya fue procesado, reiniciar para el próximo mensaje
    if "expert_selection_state" in st.session_state and st.session_state.expert_selection_state["processed"]:
        reset_expert_selection_state()
