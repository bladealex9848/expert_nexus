"""
Módulo de selección de expertos para Expert Nexus

Este módulo proporciona funciones para gestionar la selección de expertos
y el cambio entre ellos, manteniendo el contexto de la conversación.
"""

import streamlit as st
import logging
import json
from datetime import datetime

def initialize_expert_state():
    """
    Inicializa el estado para la gestión de expertos si no existe
    """
    if "expert_state" not in st.session_state:
        st.session_state.expert_state = {
            "current_expert": None,
            "expert_history": [],
            "files_by_expert": {}
        }

def get_current_expert():
    """
    Obtiene el experto actual
    """
    initialize_expert_state()
    return st.session_state.expert_state["current_expert"]

def set_current_expert(expert_key, reason="Selección manual", preserve_context=True):
    """
    Cambia el experto actual y registra el cambio en el historial
    
    Parámetros:
        expert_key: Clave del experto a establecer
        reason: Razón del cambio de experto
        preserve_context: Si se debe preservar el contexto de la conversación
    """
    initialize_expert_state()
    
    # Registrar evento para depuración
    log_expert_event(f"Intentando cambiar al experto: '{expert_key}'. Razón: {reason}", 
                    {"expert_key": expert_key, "reason": reason, "preserve_context": preserve_context})
    
    # Guardar el experto anterior
    previous_expert = st.session_state.expert_state["current_expert"]
    
    # Si hay un cambio real de experto
    if previous_expert != expert_key:
        # Preservar contexto si se solicita
        if preserve_context:
            log_expert_event("Preservando contexto de mensajes para el nuevo experto")
            # La preservación del contexto es automática en el modelo de OpenAI Assistants
            
            # Preservar archivos adjuntos si existen
            if "uploaded_files" in st.session_state:
                log_expert_event("Preservando archivos adjuntos para el nuevo experto")
                # Los archivos se mantienen en el thread
        
        # Establecer el nuevo experto
        st.session_state.expert_state["current_expert"] = expert_key
        
        # Registrar en el historial
        timestamp = datetime.now().strftime("%I:%M:%S %p")  # Formato 12 horas con AM/PM
        history_entry = {
            "timestamp": timestamp,
            "expert": expert_key,
            "reason": reason,
            "preserved_context": preserve_context
        }
        st.session_state.expert_state["expert_history"].append(history_entry)
        
        # Registrar evento para depuración
        log_expert_event("Experto cambiado exitosamente", 
                        {"previous_expert": previous_expert, 
                         "new_expert": expert_key,
                         "history_entry": history_entry})
        
        return True
    else:
        # No hubo cambio real
        log_expert_event(f"No se realizó cambio de experto (ya estaba en '{expert_key}')")
        return False

def get_expert_history():
    """
    Obtiene el historial de cambios de experto
    """
    initialize_expert_state()
    return st.session_state.expert_state["expert_history"]

def log_expert_event(message, state=None):
    """
    Registra eventos relacionados con la selección de expertos
    
    Parámetros:
        message: Mensaje descriptivo del evento
        state: Estado adicional para registrar (opcional)
    """
    initialize_expert_state()
    
    # Crear objeto de evento
    event = {
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "state": state,
        "current_expert": st.session_state.expert_state["current_expert"],
        "expert_history_length": len(st.session_state.expert_state["expert_history"])
    }
    
    # Registrar en el log
    logging.debug(json.dumps(event))
