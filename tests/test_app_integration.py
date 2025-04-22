#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de prueba para verificar la integración del módulo expert_selection con app.py.
Este script simula la interacción con la aplicación principal.
"""

import logging
import sys
import os
import time
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_app_integration.log')
    ]
)
logger = logging.getLogger("test_app_integration")

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
    
    def chat_message(self, role):
        class ChatMessage:
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass
            
            def markdown(self, text):
                logger.info(f"[CHAT] {role}: {text}")
        
        return ChatMessage()
    
    def markdown(self, text, unsafe_allow_html=False):
        logger.info(f"[MARKDOWN] {text}")

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

# Clase para simular el cliente de OpenAI
class OpenAIMock:
    def __init__(self):
        self.beta = self.Beta()
    
    class Beta:
        def __init__(self):
            self.threads = self.Threads()
        
        class Threads:
            def __init__(self):
                self.messages = self.Messages()
                self.runs = self.Runs()
            
            def create(self):
                return type('obj', (object,), {'id': 'thread_123456'})
            
            class Messages:
                def __init__(self):
                    pass
                
                def create(self, thread_id, role, content):
                    logger.info(f"[OPENAI] Creando mensaje en thread {thread_id}: {content}")
                    return True
                
                def list(self, thread_id):
                    logger.info(f"[OPENAI] Listando mensajes de thread {thread_id}")
                    return type('obj', (object,), {
                        'data': [
                            type('obj', (object,), {
                                'id': 'msg_123456',
                                'role': 'assistant',
                                'content': [
                                    type('obj', (object,), {
                                        'text': type('obj', (object,), {
                                            'value': 'Respuesta simulada del asistente'
                                        })
                                    })
                                ]
                            })
                        ]
                    })
            
            class Runs:
                def __init__(self):
                    pass
                
                def create(self, thread_id, assistant_id):
                    logger.info(f"[OPENAI] Creando run en thread {thread_id} con asistente {assistant_id}")
                    return type('obj', (object,), {'id': 'run_123456', 'status': 'queued'})
                
                def retrieve(self, thread_id, run_id):
                    logger.info(f"[OPENAI] Recuperando run {run_id} de thread {thread_id}")
                    return type('obj', (object,), {'id': run_id, 'status': 'completed'})

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

# Crear un mock para streamlit
st_mock = StreamlitMock()

# Reemplazar el módulo streamlit con nuestro mock
sys.modules['streamlit'] = st_mock

# Ahora podemos importar el módulo expert_selection
import expert_selection

# Función para simular la interacción con app.py
def simulate_app_interaction():
    logger.info("\n=== SIMULANDO INTERACCIÓN CON APP.PY ===")
    
    # Inicializar estado
    st_mock.session_state.current_expert = "asistente_virtual"
    st_mock.session_state.assistants_config = assistants_config
    st_mock.session_state.expert_history = []
    st_mock.session_state.messages = []
    st_mock.session_state.thread_id = "thread_123456"
    st_mock.session_state.client = OpenAIMock()
    
    if "expert_selection_state" in st_mock.session_state:
        st_mock.session_state.pop("expert_selection_state")
    
    # Mensaje del usuario
    user_text = "Envie un derecho de petición y no he recibido respuesta aun despues de mas de 90 días. Que puedo hacer?"
    
    # Detectar experto sugerido
    suggested_expert = expert_selection.detect_expert(user_text, {
        "tutela": ["tutela", "acción de tutela", "derecho de petición", "amparo", "protección"]
    })
    
    logger.info(f"Experto sugerido: {suggested_expert}")
    
    # Mostrar mensaje del usuario
    st_mock.session_state.messages.append({"role": "user", "content": user_text})
    with st_mock.chat_message("user"):
        st_mock.markdown(user_text)
    
    # Primera ejecución: mostrar opciones
    logger.info("\n--- Primera ejecución: mostrar opciones ---")
    continue_normal_flow, response_text = expert_selection.handle_expert_selection(user_text, suggested_expert, process_message)
    
    # Verificar que se muestran las opciones
    assert not continue_normal_flow, "Debería detener el flujo normal para mostrar opciones"
    assert response_text is None, "No debería haber respuesta en la primera ejecución"
    assert len(st_mock.info_messages) > 0, "Debería mostrar un mensaje informativo"
    assert any("¿Quieres cambiar de experto?" in msg for msg in st_mock.info_messages), "Debería preguntar si quiere cambiar de experto"
    
    # Si no debemos continuar con el flujo normal, detener la ejecución
    if not continue_normal_flow:
        if response_text:
            st_mock.rerun()
        else:
            st_mock.stop()
    
    # Simular que el usuario hace clic en "Usar experto sugerido"
    logger.info("\n--- Segunda ejecución: usuario selecciona 'Usar experto sugerido' ---")
    st_mock.session_state.expert_selection_state["choice"] = "suggested"
    
    # Segunda ejecución: procesar la selección
    continue_normal_flow, response_text = expert_selection.handle_expert_selection(user_text, suggested_expert, process_message)
    
    # Verificar que se procesa la selección
    assert not continue_normal_flow, "Debería detener el flujo normal para procesar el mensaje"
    assert response_text is not None, "Debería haber una respuesta"
    assert "tutela" in response_text.lower(), "La respuesta debería ser del experto en tutelas"
    assert st_mock.session_state.current_expert == "tutela", "El experto actual debería ser 'tutela'"
    
    # Mostrar respuesta
    st_mock.session_state.messages.append({"role": "assistant", "content": response_text, "expert": "tutela"})
    with st_mock.chat_message("assistant"):
        st_mock.markdown(f"<div class='expert-name'>TutelaBot</div>", unsafe_allow_html=True)
        st_mock.markdown(f"<div class='expert-message'>{response_text}</div>", unsafe_allow_html=True)
    
    # Verificar que se registró el cambio en el historial
    assert len(st_mock.session_state.expert_history) > 0, "Debería haber un registro en el historial"
    assert st_mock.session_state.expert_history[-1]["expert"] == "tutela", "El último registro debería ser del experto 'tutela'"
    
    # Reiniciar el estado de selección para el siguiente mensaje
    expert_selection.reset_for_new_message()
    
    # Nuevo mensaje del usuario
    user_text2 = "¿Cuál es la capital de Francia?"
    
    # No hay experto sugerido para este mensaje
    suggested_expert2 = None
    
    # Mostrar mensaje del usuario
    st_mock.session_state.messages.append({"role": "user", "content": user_text2})
    with st_mock.chat_message("user"):
        st_mock.markdown(user_text2)
    
    # Tercera ejecución: procesar directamente
    logger.info("\n--- Tercera ejecución: procesar directamente ---")
    continue_normal_flow, response_text = expert_selection.handle_expert_selection(user_text2, suggested_expert2, process_message)
    
    # Verificar que se continúa con el flujo normal
    assert continue_normal_flow, "Debería continuar con el flujo normal"
    assert response_text is None, "No debería haber respuesta en esta ejecución"
    
    # Procesar el mensaje con el experto actual
    response_text = process_message(user_text2, st_mock.session_state.current_expert)
    
    # Mostrar respuesta
    st_mock.session_state.messages.append({"role": "assistant", "content": response_text, "expert": "tutela"})
    with st_mock.chat_message("assistant"):
        st_mock.markdown(f"<div class='expert-name'>TutelaBot</div>", unsafe_allow_html=True)
        st_mock.markdown(f"<div class='expert-message'>{response_text}</div>", unsafe_allow_html=True)
    
    logger.info("\n=== SIMULACIÓN COMPLETADA ===")
    logger.info(f"Resultado: {'EXITOSO' if st_mock.session_state.current_expert == 'tutela' else 'FALLIDO'}")
    return st_mock.session_state.current_expert == "tutela"

# Función principal
def main():
    logger.info("=== INICIANDO PRUEBA DE INTEGRACIÓN CON APP.PY ===")
    
    # Simular la interacción con app.py
    result = simulate_app_interaction()
    
    # Mostrar resultado
    if result:
        logger.info("\n✅ PRUEBA DE INTEGRACIÓN COMPLETADA EXITOSAMENTE")
    else:
        logger.error("\n❌ PRUEBA DE INTEGRACIÓN FALLIDA")
    
    # Restaurar el módulo streamlit original
    import streamlit as st_original
    sys.modules['streamlit'] = st_original
    
    return result

if __name__ == "__main__":
    main()
