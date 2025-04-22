#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para probar los escenarios de selección de expertos en Expert Nexus.
Este script simula los dos escenarios principales:
1. Seleccionar el experto sugerido
2. Continuar con el experto actual
"""

import os
import time
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_expert_selection")

# Simulación de session_state de Streamlit
class SessionState:
    def __init__(self):
        self.data = {}

    def __getattr__(self, name):
        if name in self.data:
            return self.data[name]
        return None

    def __setattr__(self, name, value):
        if name == 'data':
            super().__setattr__(name, value)
        else:
            self.data[name] = value

    def __contains__(self, key):
        return key in self.data

    def pop(self, name, default=None):
        return self.data.pop(name, default)

# Simulación de funciones de Streamlit
class StreamlitMock:
    def __init__(self, session_state):
        self.session_state = session_state
        self.info_messages = []
        self.error_messages = []
        self.spinner_messages = []
        self.button_clicks = {}
        self.rerun_called = False
        self.stop_called = False

    def info(self, message):
        logger.info(f"[INFO] {message}")
        self.info_messages.append(message)

    def error(self, message):
        logger.error(f"[ERROR] {message}")
        self.error_messages.append(message)

    def spinner(self, message):
        logger.info(f"[SPINNER] {message}")
        self.spinner_messages.append(message)

        class SpinnerContext:
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

        return SpinnerContext()

    def button(self, label, key=None, use_container_width=False):
        logger.info(f"[BUTTON] {label} (key: {key})")
        return self.button_clicks.get(key, False)

    def columns(self, sizes):
        class Column:
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

        return [Column(), Column()]

    def rerun(self):
        logger.info("[RERUN] Recargando la aplicación...")
        self.rerun_called = True

    def stop(self):
        logger.info("[STOP] Deteniendo la aplicación...")
        self.stop_called = True

# Importar el módulo expert_selection
import sys
sys.path.append('.')  # Asegurarse de que podemos importar desde el directorio actual

# Crear un mock para el módulo streamlit
session_state = SessionState()
st_mock = StreamlitMock(session_state)

# Reemplazar el módulo streamlit con nuestro mock
sys.modules['streamlit'] = st_mock

# Ahora podemos importar el módulo expert_selection
import expert_selection

# Restaurar el módulo streamlit original
import streamlit as st_original
sys.modules['streamlit'] = st_original

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

# Función para procesar mensajes (simulación)
def process_message(message, expert_key):
    """Simula el procesamiento de un mensaje con un experto específico"""
    logger.info(f"Procesando mensaje con experto: {expert_key}")
    logger.info(f"Mensaje: '{message}'")
    time.sleep(1)  # Simular tiempo de procesamiento

    # Simular respuesta según el experto
    if expert_key == "tutela":
        return "Como experto en tutelas, te informo que si han pasado más de 90 días sin respuesta a tu derecho de petición, puedes interponer una acción de tutela por violación al derecho fundamental de petición."
    else:
        return f"Respuesta del experto {expert_key} a tu mensaje."

# Función para probar el escenario de selección de experto sugerido
def test_select_suggested_expert():
    logger.info("\n=== PRUEBA: SELECCIONAR EXPERTO SUGERIDO ===")

    # Inicializar estado
    session_state = SessionState()
    session_state.current_expert = "asistente_virtual"
    session_state.assistants_config = assistants_config
    session_state.expert_history = []

    # Crear un mock para streamlit
    st_mock = StreamlitMock(session_state)

    # Reemplazar temporalmente el módulo streamlit
    original_st = sys.modules.get('streamlit')
    sys.modules['streamlit'] = st_mock

    # Mensaje del usuario
    user_message = "Envie un derecho de petición y no he recibido respuesta aun despues de mas de 90 días. Que puedo hacer?"
    suggested_expert = "tutela"

    # Primera ejecución: mostrar opciones
    logger.info("\n--- Primera ejecución: mostrar opciones ---")
    continue_normal_flow, response_text = expert_selection.handle_expert_selection(user_message, suggested_expert, process_message)

    # Verificar que se muestran las opciones
    assert not continue_normal_flow, "Debería detener el flujo normal para mostrar opciones"
    assert response_text is None, "No debería haber respuesta en la primera ejecución"
    assert len(st_mock.info_messages) > 0, "Debería mostrar un mensaje informativo"
    assert "¿Quieres cambiar de experto?" in st_mock.info_messages[0], "Debería preguntar si quiere cambiar de experto"

    # Simular que el usuario hace clic en "Usar experto sugerido"
    logger.info("\n--- Segunda ejecución: usuario selecciona 'Usar experto sugerido' ---")
    st_mock.button_clicks["use_suggested"] = True

    # Segunda ejecución: procesar la selección
    continue_normal_flow, response_text = expert_selection.handle_expert_selection(user_message, suggested_expert, process_message)

    # Verificar que se procesa la selección
    assert st_mock.rerun_called, "Debería llamar a rerun() después de hacer clic en el botón"

    # Simular la recarga de la página
    logger.info("\n--- Tercera ejecución: después de rerun() ---")
    st_mock.rerun_called = False
    st_mock.button_clicks = {}  # Limpiar los clics de botones

    # Tercera ejecución: procesar el mensaje con el experto sugerido
    continue_normal_flow, response_text = expert_selection.handle_expert_selection(user_message, suggested_expert, process_message)

    # Verificar que se procesa el mensaje con el experto sugerido
    assert not continue_normal_flow, "Debería detener el flujo normal para procesar el mensaje"
    assert response_text is not None, "Debería haber una respuesta"
    assert "tutela" in response_text.lower(), "La respuesta debería ser del experto en tutelas"

    # Restaurar el módulo streamlit original
    sys.modules['streamlit'] = original_st

    logger.info("\n=== PRUEBA COMPLETADA: SELECCIONAR EXPERTO SUGERIDO ===")
    return True

# Función para probar el escenario de continuar con el experto actual
def test_continue_with_current_expert():
    logger.info("\n=== PRUEBA: CONTINUAR CON EXPERTO ACTUAL ===")

    # Inicializar estado
    session_state = SessionState()
    session_state.current_expert = "asistente_virtual"
    session_state.assistants_config = assistants_config
    session_state.expert_history = []

    # Crear un mock para streamlit
    st_mock = StreamlitMock(session_state)

    # Reemplazar temporalmente el módulo streamlit
    original_st = sys.modules.get('streamlit')
    sys.modules['streamlit'] = st_mock

    # Mensaje del usuario
    user_message = "Envie un derecho de petición y no he recibido respuesta aun despues de mas de 90 días. Que puedo hacer?"
    suggested_expert = "tutela"

    # Primera ejecución: mostrar opciones
    logger.info("\n--- Primera ejecución: mostrar opciones ---")
    continue_normal_flow, response_text = expert_selection.handle_expert_selection(user_message, suggested_expert, process_message)

    # Verificar que se muestran las opciones
    assert not continue_normal_flow, "Debería detener el flujo normal para mostrar opciones"
    assert response_text is None, "No debería haber respuesta en la primera ejecución"
    assert len(st_mock.info_messages) > 0, "Debería mostrar un mensaje informativo"
    assert "¿Quieres cambiar de experto?" in st_mock.info_messages[0], "Debería preguntar si quiere cambiar de experto"

    # Simular que el usuario hace clic en "Continuar con experto actual"
    logger.info("\n--- Segunda ejecución: usuario selecciona 'Continuar con experto actual' ---")
    st_mock.button_clicks["keep_current"] = True

    # Segunda ejecución: procesar la selección
    continue_normal_flow, response_text = expert_selection.handle_expert_selection(user_message, suggested_expert, process_message)

    # Verificar que se procesa la selección
    assert st_mock.rerun_called, "Debería llamar a rerun() después de hacer clic en el botón"

    # Simular la recarga de la página
    logger.info("\n--- Tercera ejecución: después de rerun() ---")
    st_mock.rerun_called = False
    st_mock.button_clicks = {}  # Limpiar los clics de botones

    # Tercera ejecución: procesar el mensaje con el experto actual
    continue_normal_flow, response_text = expert_selection.handle_expert_selection(user_message, suggested_expert, process_message)

    # Verificar que se procesa el mensaje con el experto actual
    assert not continue_normal_flow, "Debería detener el flujo normal para procesar el mensaje"
    assert response_text is not None, "Debería haber una respuesta"
    assert "asistente_virtual" in response_text.lower(), "La respuesta debería ser del asistente virtual"

    # Restaurar el módulo streamlit original
    sys.modules['streamlit'] = original_st

    logger.info("\n=== PRUEBA COMPLETADA: CONTINUAR CON EXPERTO ACTUAL ===")
    return True

# Función principal
def main():
    logger.info("Iniciando pruebas de escenarios de selección de expertos...")

    # Probar el escenario de selección de experto sugerido
    success_suggested = test_select_suggested_expert()

    # Probar el escenario de continuar con el experto actual
    success_current = test_continue_with_current_expert()

    # Mostrar resultados
    if success_suggested and success_current:
        logger.info("\n✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
    else:
        logger.error("\n❌ ALGUNAS PRUEBAS FALLARON")
        if not success_suggested:
            logger.error("❌ Prueba de selección de experto sugerido falló")
        if not success_current:
            logger.error("❌ Prueba de continuar con experto actual falló")

if __name__ == "__main__":
    main()
