#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de prueba automatizado para verificar el funcionamiento del módulo expert_selection.
Este script simula todo el flujo de selección de expertos sin intervención humana.
"""

import logging
import time
import sys
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_expert_selection_automated.log')
    ]
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
    def __init__(self):
        self.session_state = SessionState()
        self.info_messages = []
        self.error_messages = []
        self.success_messages = []
        self.spinner_messages = []
        self.rerun_called = False
        self.stop_called = False
    
    def info(self, message):
        logger.info(f"[INFO] {message}")
        self.info_messages.append(message)
    
    def error(self, message):
        logger.error(f"[ERROR] {message}")
        self.error_messages.append(message)
    
    def success(self, message):
        logger.info(f"[SUCCESS] {message}")
        self.success_messages.append(message)
    
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
        return False  # Siempre devuelve False, ya que simularemos los clics manualmente
    
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

# Crear un mock para streamlit
st_mock = StreamlitMock()

# Reemplazar el módulo streamlit con nuestro mock
sys.modules['streamlit'] = st_mock

# Ahora podemos importar el módulo expert_selection
import expert_selection

# Función para probar el escenario de selección de experto sugerido
def test_select_suggested_expert():
    logger.info("\n=== PRUEBA: SELECCIONAR EXPERTO SUGERIDO ===")
    
    # Inicializar estado
    st_mock.session_state.current_expert = "asistente_virtual"
    st_mock.session_state.assistants_config = assistants_config
    st_mock.session_state.expert_history = []
    
    if "expert_selection_state" in st_mock.session_state:
        st_mock.session_state.pop("expert_selection_state")
    
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
    assert any("¿Quieres cambiar de experto?" in msg for msg in st_mock.info_messages), "Debería preguntar si quiere cambiar de experto"
    
    # Simular que el usuario hace clic en "Usar experto sugerido"
    logger.info("\n--- Segunda ejecución: usuario selecciona 'Usar experto sugerido' ---")
    st_mock.session_state.expert_selection_state["choice"] = "suggested"
    
    # Segunda ejecución: procesar la selección
    continue_normal_flow, response_text = expert_selection.handle_expert_selection(user_message, suggested_expert, process_message)
    
    # Verificar que se procesa la selección
    assert not continue_normal_flow, "Debería detener el flujo normal para procesar el mensaje"
    assert response_text is not None, "Debería haber una respuesta"
    assert "tutela" in response_text.lower(), "La respuesta debería ser del experto en tutelas"
    assert st_mock.session_state.current_expert == "tutela", "El experto actual debería ser 'tutela'"
    
    # Verificar que se registró el cambio en el historial
    assert len(st_mock.session_state.expert_history) > 0, "Debería haber un registro en el historial"
    assert st_mock.session_state.expert_history[-1]["expert"] == "tutela", "El último registro debería ser del experto 'tutela'"
    
    logger.info("\n=== PRUEBA COMPLETADA: SELECCIONAR EXPERTO SUGERIDO ===")
    logger.info(f"Resultado: {'EXITOSO' if st_mock.session_state.current_expert == 'tutela' else 'FALLIDO'}")
    return st_mock.session_state.current_expert == "tutela"

# Función para probar el escenario de continuar con el experto actual
def test_continue_with_current_expert():
    logger.info("\n=== PRUEBA: CONTINUAR CON EXPERTO ACTUAL ===")
    
    # Inicializar estado
    st_mock.session_state.current_expert = "asistente_virtual"
    st_mock.session_state.assistants_config = assistants_config
    st_mock.session_state.expert_history = []
    
    if "expert_selection_state" in st_mock.session_state:
        st_mock.session_state.pop("expert_selection_state")
    
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
    assert any("¿Quieres cambiar de experto?" in msg for msg in st_mock.info_messages), "Debería preguntar si quiere cambiar de experto"
    
    # Simular que el usuario hace clic en "Continuar con experto actual"
    logger.info("\n--- Segunda ejecución: usuario selecciona 'Continuar con experto actual' ---")
    st_mock.session_state.expert_selection_state["choice"] = "current"
    
    # Segunda ejecución: procesar la selección
    continue_normal_flow, response_text = expert_selection.handle_expert_selection(user_message, suggested_expert, process_message)
    
    # Verificar que se procesa la selección
    assert not continue_normal_flow, "Debería detener el flujo normal para procesar el mensaje"
    assert response_text is not None, "Debería haber una respuesta"
    assert "asistente_virtual" in response_text.lower(), "La respuesta debería ser del asistente virtual"
    assert st_mock.session_state.current_expert == "asistente_virtual", "El experto actual debería seguir siendo 'asistente_virtual'"
    
    logger.info("\n=== PRUEBA COMPLETADA: CONTINUAR CON EXPERTO ACTUAL ===")
    logger.info(f"Resultado: {'EXITOSO' if st_mock.session_state.current_expert == 'asistente_virtual' else 'FALLIDO'}")
    return st_mock.session_state.current_expert == "asistente_virtual"

# Función para probar el escenario sin experto sugerido
def test_no_suggested_expert():
    logger.info("\n=== PRUEBA: SIN EXPERTO SUGERIDO ===")
    
    # Inicializar estado
    st_mock.session_state.current_expert = "asistente_virtual"
    st_mock.session_state.assistants_config = assistants_config
    st_mock.session_state.expert_history = []
    
    if "expert_selection_state" in st_mock.session_state:
        st_mock.session_state.pop("expert_selection_state")
    
    # Mensaje del usuario
    user_message = "¿Cuál es la capital de Francia?"
    suggested_expert = None
    
    # Ejecución: procesar directamente
    logger.info("\n--- Ejecución: procesar directamente ---")
    continue_normal_flow, response_text = expert_selection.handle_expert_selection(user_message, suggested_expert, process_message)
    
    # Verificar que se continúa con el flujo normal
    assert continue_normal_flow, "Debería continuar con el flujo normal"
    assert response_text is None, "No debería haber respuesta en esta ejecución"
    assert st_mock.session_state.current_expert == "asistente_virtual", "El experto actual debería seguir siendo 'asistente_virtual'"
    
    # Simular el procesamiento del mensaje con el experto actual
    response_text = process_message(user_message, st_mock.session_state.current_expert)
    
    # Verificar que se procesa el mensaje con el experto actual
    assert response_text is not None, "Debería haber una respuesta"
    assert "asistente_virtual" in response_text.lower(), "La respuesta debería ser del asistente virtual"
    
    logger.info("\n=== PRUEBA COMPLETADA: SIN EXPERTO SUGERIDO ===")
    logger.info(f"Resultado: {'EXITOSO' if st_mock.session_state.current_expert == 'asistente_virtual' else 'FALLIDO'}")
    return st_mock.session_state.current_expert == "asistente_virtual"

# Función para probar el escenario de cambio de experto con múltiples mensajes
def test_multiple_messages():
    logger.info("\n=== PRUEBA: MÚLTIPLES MENSAJES ===")
    
    # Inicializar estado
    st_mock.session_state.current_expert = "asistente_virtual"
    st_mock.session_state.assistants_config = assistants_config
    st_mock.session_state.expert_history = []
    
    if "expert_selection_state" in st_mock.session_state:
        st_mock.session_state.pop("expert_selection_state")
    
    # Primer mensaje: cambiar a experto en tutela
    user_message1 = "Envie un derecho de petición y no he recibido respuesta aun despues de mas de 90 días. Que puedo hacer?"
    suggested_expert1 = "tutela"
    
    # Primera ejecución: mostrar opciones
    logger.info("\n--- Primera ejecución: mostrar opciones para mensaje 1 ---")
    continue_normal_flow, response_text = expert_selection.handle_expert_selection(user_message1, suggested_expert1, process_message)
    
    # Verificar que se muestran las opciones
    assert not continue_normal_flow, "Debería detener el flujo normal para mostrar opciones"
    
    # Simular que el usuario hace clic en "Usar experto sugerido"
    logger.info("\n--- Segunda ejecución: usuario selecciona 'Usar experto sugerido' para mensaje 1 ---")
    st_mock.session_state.expert_selection_state["choice"] = "suggested"
    
    # Segunda ejecución: procesar la selección
    continue_normal_flow, response_text = expert_selection.handle_expert_selection(user_message1, suggested_expert1, process_message)
    
    # Verificar que se procesa la selección
    assert not continue_normal_flow, "Debería detener el flujo normal para procesar el mensaje"
    assert st_mock.session_state.current_expert == "tutela", "El experto actual debería ser 'tutela'"
    
    # Reiniciar el estado de selección para el siguiente mensaje
    expert_selection.reset_for_new_message()
    
    # Segundo mensaje: cambiar a experto en transformación digital
    user_message2 = "Necesito implementar una estrategia de transformación digital en mi empresa"
    suggested_expert2 = "transformacion_digital"
    
    # Tercera ejecución: mostrar opciones para el segundo mensaje
    logger.info("\n--- Tercera ejecución: mostrar opciones para mensaje 2 ---")
    continue_normal_flow, response_text = expert_selection.handle_expert_selection(user_message2, suggested_expert2, process_message)
    
    # Verificar que se muestran las opciones
    assert not continue_normal_flow, "Debería detener el flujo normal para mostrar opciones"
    
    # Simular que el usuario hace clic en "Usar experto sugerido"
    logger.info("\n--- Cuarta ejecución: usuario selecciona 'Usar experto sugerido' para mensaje 2 ---")
    st_mock.session_state.expert_selection_state["choice"] = "suggested"
    
    # Cuarta ejecución: procesar la selección
    continue_normal_flow, response_text = expert_selection.handle_expert_selection(user_message2, suggested_expert2, process_message)
    
    # Verificar que se procesa la selección
    assert not continue_normal_flow, "Debería detener el flujo normal para procesar el mensaje"
    assert st_mock.session_state.current_expert == "transformacion_digital", "El experto actual debería ser 'transformacion_digital'"
    
    # Verificar que se registraron los cambios en el historial
    assert len(st_mock.session_state.expert_history) == 2, "Debería haber dos registros en el historial"
    assert st_mock.session_state.expert_history[0]["expert"] == "tutela", "El primer registro debería ser del experto 'tutela'"
    assert st_mock.session_state.expert_history[1]["expert"] == "transformacion_digital", "El segundo registro debería ser del experto 'transformacion_digital'"
    
    logger.info("\n=== PRUEBA COMPLETADA: MÚLTIPLES MENSAJES ===")
    logger.info(f"Resultado: {'EXITOSO' if st_mock.session_state.current_expert == 'transformacion_digital' else 'FALLIDO'}")
    return st_mock.session_state.current_expert == "transformacion_digital"

# Función para probar el escenario de manejo de errores
def test_error_handling():
    logger.info("\n=== PRUEBA: MANEJO DE ERRORES ===")
    
    # Inicializar estado
    st_mock.session_state.current_expert = "asistente_virtual"
    st_mock.session_state.assistants_config = assistants_config
    st_mock.session_state.expert_history = []
    
    if "expert_selection_state" in st_mock.session_state:
        st_mock.session_state.pop("expert_selection_state")
    
    # Mensaje del usuario
    user_message = "Envie un derecho de petición y no he recibido respuesta aun despues de mas de 90 días. Que puedo hacer?"
    suggested_expert = "experto_inexistente"  # Experto que no existe
    
    # Ejecución: procesar directamente
    logger.info("\n--- Ejecución: procesar con experto inexistente ---")
    continue_normal_flow, response_text = expert_selection.handle_expert_selection(user_message, suggested_expert, process_message)
    
    # Verificar que se continúa con el flujo normal
    assert continue_normal_flow, "Debería continuar con el flujo normal"
    assert response_text is None, "No debería haber respuesta en esta ejecución"
    assert st_mock.session_state.current_expert == "asistente_virtual", "El experto actual debería seguir siendo 'asistente_virtual'"
    
    # Simular el procesamiento del mensaje con el experto actual
    response_text = process_message(user_message, st_mock.session_state.current_expert)
    
    # Verificar que se procesa el mensaje con el experto actual
    assert response_text is not None, "Debería haber una respuesta"
    assert "asistente_virtual" in response_text.lower(), "La respuesta debería ser del asistente virtual"
    
    logger.info("\n=== PRUEBA COMPLETADA: MANEJO DE ERRORES ===")
    logger.info(f"Resultado: {'EXITOSO' if st_mock.session_state.current_expert == 'asistente_virtual' else 'FALLIDO'}")
    return st_mock.session_state.current_expert == "asistente_virtual"

# Función principal
def main():
    logger.info("=== INICIANDO PRUEBAS AUTOMATIZADAS DE SELECCIÓN DE EXPERTOS ===")
    
    # Ejecutar todas las pruebas
    results = {
        "Seleccionar experto sugerido": test_select_suggested_expert(),
        "Continuar con experto actual": test_continue_with_current_expert(),
        "Sin experto sugerido": test_no_suggested_expert(),
        "Múltiples mensajes": test_multiple_messages(),
        "Manejo de errores": test_error_handling()
    }
    
    # Mostrar resultados
    logger.info("\n=== RESULTADOS DE LAS PRUEBAS ===")
    all_passed = True
    for test_name, result in results.items():
        logger.info(f"{test_name}: {'EXITOSO' if result else 'FALLIDO'}")
        if not result:
            all_passed = False
    
    if all_passed:
        logger.info("\n✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
    else:
        logger.error("\n❌ ALGUNAS PRUEBAS FALLARON")
    
    # Restaurar el módulo streamlit original
    import streamlit as st_original
    sys.modules['streamlit'] = st_original
    
    return all_passed

if __name__ == "__main__":
    main()
