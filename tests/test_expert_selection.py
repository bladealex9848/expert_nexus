#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de prueba para simular el flujo de selección de expertos en Expert Nexus.
Este script simula el comportamiento de Streamlit y permite probar la lógica
de selección de expertos en un entorno controlado.
"""

import os
import time
from datetime import datetime

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

    def pop(self, name, default=None):
        return self.data.pop(name, default)

# Simulación de funciones de Streamlit
def info(message):
    print(f"\n[INFO] {message}")

def spinner(message):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"\n[SPINNER] {message}")
            result = func(*args, **kwargs)
            print(f"[SPINNER] Completado")
            return result
        return wrapper
    return decorator

def button(label, key=None):
    print(f"\n[BUTTON] {label} (key: {key})")
    choice = input("¿Presionar este botón? (s/n): ")
    return choice.lower() == 's'

def rerun():
    print("\n[RERUN] Recargando la aplicación...")
    time.sleep(1)
    print("=" * 50)
    # En lugar de llamar a main() directamente, que podría causar una recursión infinita,
    # simplemente indicamos que queremos continuar y dejamos que el flujo principal maneje esto
    return True

def columns(sizes):
    class Column:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
    return [Column(), Column()]

# Simulación de funciones de la aplicación
def detect_expert(message):
    """Simula la detección de experto basada en palabras clave"""
    if "derecho de petición" in message.lower() or "tutela" in message.lower():
        return "tutela"
    elif "inteligencia artificial" in message.lower() or "ia" in message.lower():
        return "inteligencia_artificial"
    return None

def change_expert(expert_key, reason="Selección manual"):
    """Simula el cambio de experto"""
    print(f"\n[CHANGE_EXPERT] Cambiando a experto: {expert_key}, Razón: {reason}")
    session_state.current_expert = expert_key
    session_state.expert_history.append({
        "timestamp": datetime.now().strftime("%I:%M:%S %p"),
        "expert": expert_key,
        "reason": reason
    })
    return True

def process_message(message, expert_key):
    """Simula el procesamiento de un mensaje con un experto específico"""
    print(f"\n[PROCESS_MESSAGE] Procesando mensaje con experto: {expert_key}")
    print(f"Mensaje: '{message}'")
    time.sleep(1)  # Simular tiempo de procesamiento

    # Simular respuesta según el experto
    if expert_key == "tutela":
        return "Como experto en tutelas, te informo que si han pasado más de 90 días sin respuesta a tu derecho de petición, puedes interponer una acción de tutela por violación al derecho fundamental de petición."
    elif expert_key == "inteligencia_artificial":
        return "Como experto en IA, puedo explicarte cómo funcionan los algoritmos de aprendizaje automático."
    else:
        return f"Respuesta del experto {expert_key} a tu mensaje."

# Inicialización del estado
session_state = SessionState()

# Configuración de expertos disponibles
assistants_config = {
    "tutela": {
        "id": "asst_xisQZwJ1bbmvXET8YG0eiAmb",
        "titulo": "TutelaBot - Asistente Especializado en Acción de Tutela y Derecho de Petición",
        "descripcion": "Experto en mecanismos constitucionales de protección de derechos"
    },
    "inteligencia_artificial": {
        "id": "asst_MzMayuSJV8AhP6vacv2ee3Xx",
        "titulo": "Asistente de Inteligencia Artificial",
        "descripcion": "Especialista en IA, aprendizaje automático y resolución de problemas"
    },
    "asistente_virtual": {
        "id": "asst_RfRNo5Ij76ieg7mV11CqYV9v",
        "titulo": "Asistente Virtual de Inteligencia Artificial",
        "descripcion": "Ayudante virtual con conocimiento amplio en múltiples disciplinas"
    }
}

def initialize_session():
    """Inicializa el estado de la sesión si es necesario"""
    # Inicializar mensajes
    if not hasattr(session_state, 'messages') or session_state.messages is None:
        session_state.messages = []

    # Inicializar historial de expertos
    if not hasattr(session_state, 'expert_history') or session_state.expert_history is None:
        session_state.expert_history = []

    # Inicializar experto actual
    if not hasattr(session_state, 'current_expert') or session_state.current_expert is None:
        default_expert = "asistente_virtual"
        session_state.current_expert = default_expert
        if session_state.expert_history is None:
            session_state.expert_history = []
        session_state.expert_history.append({
            "timestamp": datetime.now().strftime("%I:%M:%S %p"),
            "expert": default_expert,
            "reason": "Inicio de conversación"
        })

    # Variables para el manejo de la selección de experto
    if not hasattr(session_state, 'expert_selection_pending') or session_state.expert_selection_pending is None:
        session_state.expert_selection_pending = False
        session_state.pending_message = ""
        session_state.suggested_expert_id = ""

def show_expert_history():
    """Muestra el historial de expertos"""
    print("\n[HISTORIAL DE EXPERTOS]")
    for entry in session_state.expert_history:
        expert_key = entry["expert"]
        if expert_key in assistants_config:
            expert_title = assistants_config[expert_key]["titulo"]
            print(f"{entry['timestamp']}: {expert_title} - {entry['reason']}")

def show_messages():
    """Muestra los mensajes de la conversación"""
    print("\n[MENSAJES]")
    for msg in session_state.messages:
        role = "Usuario" if msg["role"] == "user" else "Asistente"
        print(f"{role}: {msg['content']}")
        if role == "Asistente" and "expert" in msg:
            expert_key = msg["expert"]
            if expert_key in assistants_config:
                print(f"(Respondido por: {assistants_config[expert_key]['titulo']})")
        print("-" * 50)

def process_user_input():
    """Procesa la entrada del usuario y maneja la selección de expertos"""
    # Mostrar información del experto actual
    current_expert_key = session_state.current_expert
    current_expert = assistants_config[current_expert_key]
    print(f"\n[EXPERTO ACTUAL] {current_expert['titulo']}")
    print(f"Descripción: {current_expert['descripcion']}")

    # Solicitar entrada del usuario
    if not hasattr(session_state, 'pending_user_input') or not session_state.pending_user_input:
        user_text = input("\nEscribe tu mensaje (o 'salir' para terminar): ")
        if user_text.lower() == 'salir':
            return False

        # Guardar el mensaje del usuario
        session_state.messages.append({"role": "user", "content": user_text})

        # Detectar si es necesario cambiar de experto
        suggested_expert = detect_expert(user_text)

        # Procesar la respuesta
        if suggested_expert and suggested_expert != session_state.current_expert:
            # Verificar que el experto sugerido exista
            if suggested_expert in assistants_config:
                expert_titulo = assistants_config[suggested_expert]["titulo"]

                # Inicializar variables de estado para el manejo de la selección
                if not hasattr(session_state, 'expert_selection_pending'):
                    session_state.expert_selection_pending = False
                    session_state.pending_message = ""
                    session_state.suggested_expert_id = ""

                # Si ya hay una selección pendiente, procesar según la elección
                if session_state.expert_selection_pending and session_state.pending_message == user_text:
                    if hasattr(session_state, 'expert_choice'):
                        if session_state.expert_choice == "suggested":
                            # Usar el experto sugerido
                            @spinner(f"Procesando tu mensaje con {assistants_config[session_state.suggested_expert_id]['titulo']}...")
                            def process_with_suggested():
                                change_expert(session_state.suggested_expert_id, "Cambio automático por palabras clave")
                                response_text = process_message(user_text, session_state.suggested_expert_id)
                                # Guardar la respuesta
                                session_state.messages.append({
                                    "role": "assistant",
                                    "content": response_text,
                                    "expert": session_state.suggested_expert_id
                                })
                                # Limpiar el estado de selección
                                session_state.expert_selection_pending = False
                                session_state.pending_message = ""
                                session_state.suggested_expert_id = ""
                                session_state.pop('expert_choice', None)
                                session_state.pending_user_input = False
                                return True

                            return process_with_suggested()

                        elif session_state.expert_choice == "current":
                            # Continuar con el experto actual
                            @spinner(f"Procesando tu mensaje con {assistants_config[session_state.current_expert]['titulo']}...")
                            def process_with_current():
                                response_text = process_message(user_text, session_state.current_expert)
                                # Guardar la respuesta
                                session_state.messages.append({
                                    "role": "assistant",
                                    "content": response_text,
                                    "expert": session_state.current_expert
                                })
                                # Limpiar el estado de selección
                                session_state.expert_selection_pending = False
                                session_state.pending_message = ""
                                session_state.suggested_expert_id = ""
                                session_state.pop('expert_choice', None)
                                session_state.pending_user_input = False
                                return True

                            return process_with_current()
                else:
                    # Mostrar opciones de selección de experto
                    info(f"Tu mensaje parece relacionado con '{expert_titulo}'. ¿Quieres cambiar de experto?")

                    # Guardar información para la próxima ejecución
                    session_state.expert_selection_pending = True
                    session_state.pending_message = user_text
                    session_state.suggested_expert_id = suggested_expert
                    session_state.pending_user_input = True

                    # Mostrar botones de selección
                    col1, col2 = columns([1, 1])
                    with col1:
                        if button("Usar experto sugerido", key="use_suggested"):
                            session_state.expert_choice = "suggested"
                            return True
                    with col2:
                        if button("Continuar con experto actual", key="keep_current"):
                            session_state.expert_choice = "current"
                            return True

                    # Si no se seleccionó ninguna opción, mantener el estado pendiente
                    return True
            else:
                # Si el experto sugerido no existe, procesar con el experto actual
                print(f"\n[WARNING] Experto sugerido '{suggested_expert}' no encontrado en la configuración")
                @spinner(f"Procesando tu mensaje con {assistants_config[session_state.current_expert]['titulo']}...")
                def process_with_current_fallback():
                    response_text = process_message(user_text, session_state.current_expert)
                    # Guardar la respuesta
                    session_state.messages.append({
                        "role": "assistant",
                        "content": response_text,
                        "expert": session_state.current_expert
                    })
                    session_state.pending_user_input = False
                    return True

                return process_with_current_fallback()
        else:
            # Procesar con el experto actual
            @spinner(f"Procesando tu mensaje con {assistants_config[session_state.current_expert]['titulo']}...")
            def process_with_current_direct():
                response_text = process_message(user_text, session_state.current_expert)
                # Guardar la respuesta
                session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "expert": session_state.current_expert
                })
                session_state.pending_user_input = False
                return True

            return process_with_current_direct()
    else:
        # Si hay una entrada pendiente, mostrar mensaje de espera
        print("\n[ESPERANDO] Por favor, selecciona una opción para continuar.")
        return True

def main():
    """Función principal del script de prueba"""
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 50)
        print("SIMULADOR DE SELECCIÓN DE EXPERTOS - EXPERT NEXUS")
        print("=" * 50)

        # Inicializar el estado de la sesión
        initialize_session()

        # Mostrar información actual
        show_expert_history()
        show_messages()

        # Procesar la entrada del usuario
        continue_running = process_user_input()

        if not continue_running:
            print("\n¡Gracias por usar el simulador de Expert Nexus!")
            return

        # Opción para continuar o salir
        if not hasattr(session_state, 'pending_user_input') or not session_state.pending_user_input:
            choice = input("\n¿Continuar con otra consulta? (s/n): ")
            if choice.lower() == 's':
                # Reiniciar el flujo
                print("\n[RERUN] Recargando la aplicación...")
                time.sleep(1)
                print("=" * 50)
                main()  # Llamada recursiva controlada
            else:
                print("\n¡Gracias por usar el simulador de Expert Nexus!")
    except Exception as e:
        print(f"\n[ERROR] Se produjo un error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
