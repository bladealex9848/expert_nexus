#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo para manejar la selección de expertos en Expert Nexus.
Este módulo contiene funciones para detectar y cambiar expertos,
así como para manejar el flujo de selección de expertos.
"""

import streamlit as st
import logging
import os
import json
from datetime import datetime

# Configurar logging específico para este módulo
logger = logging.getLogger('expert_selection')
logger.setLevel(logging.DEBUG)

# Crear un manejador para el archivo de log
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(log_dir, 'expert_selection.log'))
file_handler.setLevel(logging.DEBUG)

# Definir el formato del log
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Agregar el manejador al logger
logger.addHandler(file_handler)

# Función para registrar el estado completo
def log_state(message, state=None):
    """Registra un mensaje y el estado actual en el archivo de log."""
    if state is None and hasattr(st, 'session_state') and 'expert_selection_state' in st.session_state:
        state = st.session_state.expert_selection_state

    log_entry = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
        'message': message,
        'state': state
    }

    # Agregar información adicional si está disponible
    if hasattr(st, 'session_state'):
        if 'current_expert' in st.session_state:
            log_entry['current_expert'] = st.session_state.current_expert
        if 'expert_history' in st.session_state:
            log_entry['expert_history_length'] = len(st.session_state.expert_history)

    logger.debug(json.dumps(log_entry, default=str))

def initialize_expert_selection_state():
    """
    Inicializa las variables de estado necesarias para la selección de expertos.
    """
    if "expert_selection_state" not in st.session_state:
        log_state("Inicializando estado de selección de expertos")
        st.session_state.expert_selection_state = {
            "pending": False,
            "message": "",
            "suggested_expert": "",
            "choice": None,
            "processed": False
        }
        log_state("Estado de selección de expertos inicializado", st.session_state.expert_selection_state)
    else:
        log_state(f"Estado de selección de expertos ya existe", st.session_state.expert_selection_state)

def reset_expert_selection_state():
    """
    Reinicia el estado de selección de expertos.
    """
    log_state("Reiniciando estado de selección de expertos")
    if "expert_selection_state" in st.session_state:
        # Guardar el estado anterior para el log
        old_state = dict(st.session_state.expert_selection_state)

        # Reiniciar el estado
        st.session_state.expert_selection_state = {
            "pending": False,
            "message": "",
            "suggested_expert": "",
            "choice": None,
            "processed": False
        }

        log_state("Estado de selección de expertos reiniciado", {
            "old_state": old_state,
            "new_state": st.session_state.expert_selection_state
        })

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

def change_expert(expert_key, reason="Selección manual", preserve_context=True):
    """
    Cambia el experto actual y registra el cambio en el historial.

    Parámetros:
        expert_key: Clave del experto al que se cambiará
        reason: Razón del cambio de experto
        preserve_context: Si se debe preservar el contexto (mensajes y archivos) entre cambios

    Retorno:
        bool: True si el cambio fue exitoso, False en caso contrario
    """
    try:
        log_state(f"Intentando cambiar al experto: '{expert_key}'. Razón: {reason}", {
            "expert_key": expert_key,
            "reason": reason,
            "preserve_context": preserve_context
        })

        # Verificar que el experto exista
        if not hasattr(st.session_state, 'assistants_config'):
            log_state(f"Error: st.session_state no tiene el atributo 'assistants_config'")
            return False

        if expert_key not in st.session_state.assistants_config:
            log_state(f"Error: Experto '{expert_key}' no encontrado en la configuración")
            return False

        # Guardar el experto anterior para el log
        previous_expert = st.session_state.current_expert if hasattr(st.session_state, 'current_expert') else None

        # Siempre preservar el contexto de mensajes (chat)
        if hasattr(st.session_state, 'messages'):
            log_state(f"Preservando contexto de mensajes para el nuevo experto")
            # Los mensajes ya están en st.session_state.messages, no es necesario hacer nada más

        # Guardar los archivos adjuntos si es necesario
        if preserve_context and hasattr(st.session_state, 'uploaded_files'):
            log_state(f"Preservando archivos adjuntos para el nuevo experto")
            # Los archivos ya están en st.session_state.uploaded_files, no es necesario hacer nada más
        elif not preserve_context and hasattr(st.session_state, 'uploaded_files') and st.session_state.uploaded_files:
            log_state(f"Limpiando archivos adjuntos al cambiar de experto")
            # Guardar los archivos para el log
            previous_files = list(st.session_state.uploaded_files)
            # Limpiar los archivos
            st.session_state.uploaded_files = []
            # Limpiar el contenido de los documentos si existe
            if hasattr(st.session_state, 'document_contents'):
                st.session_state.document_contents = {}

        # Cambiar el experto actual
        st.session_state.current_expert = expert_key

        # Inicializar el historial de expertos si no existe
        if not hasattr(st.session_state, 'expert_history'):
            st.session_state.expert_history = []

        # Registrar el cambio en el historial
        history_entry = {
            "timestamp": datetime.now().strftime("%I:%M:%S %p"),
            "expert": expert_key,
            "reason": reason,
            "preserved_context": preserve_context
        }
        st.session_state.expert_history.append(history_entry)

        log_state(f"Experto cambiado exitosamente", {
            "previous_expert": previous_expert,
            "new_expert": expert_key,
            "history_entry": history_entry
        })
        return True
    except Exception as e:
        log_state(f"Error al cambiar de experto: {str(e)}", {
            "error": str(e),
            "expert_key": expert_key
        })
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

    log_state(f"Iniciando handle_expert_selection", {
        "user_text": user_text[:50] + "..." if len(user_text) > 50 else user_text,
        "suggested_expert": suggested_expert,
        "function_id": id(process_message_func)
    })

    # Si no hay un experto sugerido o es el mismo que el actual, continuar con el flujo normal
    if not suggested_expert:
        log_state("No hay experto sugerido, continuando con flujo normal")
        return True, None

    if hasattr(st.session_state, 'current_expert') and suggested_expert == st.session_state.current_expert:
        log_state("El experto sugerido es el mismo que el actual, continuando con flujo normal")
        return True, None

    # Verificar que el experto sugerido exista
    if not hasattr(st.session_state, 'assistants_config'):
        log_state("Error: st.session_state no tiene el atributo 'assistants_config'")
        return True, None

    if suggested_expert not in st.session_state.assistants_config:
        log_state(f"Error: Experto sugerido '{suggested_expert}' no encontrado en la configuración")
        return True, None

    # Obtener el título del experto sugerido
    expert_titulo = st.session_state.assistants_config[suggested_expert]["titulo"]
    log_state(f"Título del experto sugerido: {expert_titulo}")

    # Estado actual de la selección de expertos
    selection_state = st.session_state.expert_selection_state
    log_state("Estado actual de selección", selection_state)

    # Si ya se procesó esta selección, continuar con el flujo normal
    if selection_state["processed"] and selection_state["message"] == user_text:
        log_state("Esta selección ya fue procesada, continuando con flujo normal")
        # Reiniciar el estado para futuros mensajes
        reset_expert_selection_state()
        return True, None

    # Si hay una selección pendiente para este mensaje
    if selection_state["pending"] and selection_state["message"] == user_text:
        log_state(f"Hay una selección pendiente para este mensaje", {
            "choice": selection_state['choice'],
            "message": selection_state['message'],
            "suggested_expert": selection_state['suggested_expert']
        })

        # Si se ha hecho una elección
        if selection_state["choice"] is not None:
            try:
                if selection_state["choice"] == "suggested":
                    log_state(f"Usuario eligió usar el experto sugerido", {
                        "suggested_expert": selection_state['suggested_expert']
                    })

                    # Usar el experto sugerido
                    with st.spinner(f"Procesando tu mensaje con {st.session_state.assistants_config[selection_state['suggested_expert']]['titulo']}..."):
                        # Guardar el experto sugerido en una variable local para asegurarnos de que no cambie
                        suggested_expert_key = selection_state["suggested_expert"]
                        log_state(f"Experto sugerido guardado en variable local: {suggested_expert_key}")

                        # Cambiar al experto sugerido
                        success = change_expert(suggested_expert_key, "Cambio automático por palabras clave")
                        log_state(f"Resultado del cambio de experto: {success}")

                        if not success:
                            log_state(f"No se pudo cambiar al experto sugerido: {suggested_expert_key}")
                            st.error(f"No se pudo cambiar al experto sugerido. Continuando con el experto actual.")
                            # Procesar con el experto actual como fallback
                            current_expert = st.session_state.current_expert
                            log_state(f"Procesando con experto actual como fallback: {current_expert}")
                            response_text = process_message_func(user_text, current_expert)
                        else:
                            # Verificar que el cambio de experto se haya realizado correctamente
                            if st.session_state.current_expert != suggested_expert_key:
                                log_state(f"El cambio de experto no se reflejó correctamente", {
                                    "esperado": suggested_expert_key,
                                    "actual": st.session_state.current_expert
                                })

                                # Forzar el cambio de experto nuevamente
                                st.session_state.current_expert = suggested_expert_key
                                log_state(f"Experto forzado a: {st.session_state.current_expert}")

                            # Procesar el mensaje con el experto sugerido
                            log_state(f"Procesando mensaje con experto: {suggested_expert_key}")
                            response_text = process_message_func(user_text, suggested_expert_key)

                        log_state(f"Respuesta obtenida", {
                            "success": response_text is not None,
                            "current_expert": st.session_state.current_expert
                        })

                        # Marcar como procesado
                        selection_state["processed"] = True
                        log_state("Marcado como procesado", selection_state)

                        # Devolver la respuesta
                        return False, response_text
                elif selection_state["choice"] == "current":
                    log_state("Usuario eligió continuar con el experto actual")

                    # Continuar con el experto actual
                    with st.spinner(f"Procesando tu mensaje con {st.session_state.assistants_config[st.session_state.current_expert]['titulo']}..."):
                        # Procesar el mensaje con el experto actual
                        current_expert = st.session_state.current_expert
                        log_state(f"Procesando mensaje con experto actual: {current_expert}")
                        response_text = process_message_func(user_text, current_expert)

                        log_state(f"Respuesta obtenida", {
                            "success": response_text is not None,
                            "current_expert": current_expert
                        })

                        # Marcar como procesado
                        selection_state["processed"] = True
                        log_state("Marcado como procesado", selection_state)

                        # Devolver la respuesta
                        return False, response_text
            except Exception as e:
                log_state(f"Error al procesar la selección de experto: {str(e)}", {
                    "error": str(e),
                    "traceback": str(e.__traceback__)
                })
                st.error(f"Ocurrió un error al procesar tu mensaje. Por favor, inténtalo de nuevo.")
                # Reiniciar el estado para evitar bucles
                reset_expert_selection_state()
                return True, None
    else:
        log_state(f"Mostrando opciones de selección para el experto", {
            "suggested_expert": suggested_expert,
            "expert_titulo": expert_titulo
        })

        # Mostrar opciones de selección de experto
        st.info(f"Tu mensaje parece relacionado con '{expert_titulo}'. ¿Quieres cambiar de experto?")

        # Guardar información para la próxima ejecución
        old_state = dict(selection_state)
        selection_state["pending"] = True
        selection_state["message"] = user_text
        selection_state["suggested_expert"] = suggested_expert
        selection_state["choice"] = None
        selection_state["processed"] = False

        log_state(f"Estado guardado para la próxima ejecución", {
            "old_state": old_state,
            "new_state": selection_state
        })

        # Mostrar botones de selección
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Usar experto sugerido", key="use_suggested", use_container_width=True):
                log_state(f"Botón 'Usar experto sugerido' presionado")
                selection_state["choice"] = "suggested"
                log_state(f"Estado actualizado después de presionar 'Usar experto sugerido'", selection_state)
                st.rerun()
        with col2:
            if st.button("Continuar con experto actual", key="keep_current", use_container_width=True):
                log_state(f"Botón 'Continuar con experto actual' presionado")
                selection_state["choice"] = "current"
                log_state(f"Estado actualizado después de presionar 'Continuar con experto actual'", selection_state)
                st.rerun()

        # Detener el flujo normal
        log_state("Deteniendo flujo normal para mostrar opciones de selección")
        return False, None

    # Por defecto, continuar con el flujo normal
    log_state("Continuando con flujo normal (caso por defecto)")
    return True, None

def reset_for_new_message():
    """
    Reinicia el estado de selección de expertos para un nuevo mensaje.
    """
    # Si el mensaje actual ya fue procesado, reiniciar para el próximo mensaje
    if "expert_selection_state" in st.session_state:
        log_state("Evaluando si reiniciar el estado para un nuevo mensaje", st.session_state.expert_selection_state)

        if st.session_state.expert_selection_state["processed"]:
            log_state("Reiniciando estado de selección para un nuevo mensaje (mensaje procesado)")
            reset_expert_selection_state()
        elif st.session_state.expert_selection_state["pending"] and not st.session_state.expert_selection_state["choice"]:
            # Si hay una selección pendiente pero no se ha hecho una elección, mantener el estado
            log_state("Manteniendo estado de selección pendiente para continuar el flujo")
            pass
        else:
            # En otros casos, reiniciar para evitar estados inconsistentes
            log_state("Reiniciando estado de selección para un nuevo mensaje (caso general)")
            reset_expert_selection_state()
