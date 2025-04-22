#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script simplificado para probar el flujo de selección de expertos.
"""

import time
from datetime import datetime

# Simulación de estado de sesión
class SessionState:
    def __init__(self):
        self.current_expert = "asistente_virtual"
        self.expert_history = []
        self.messages = []
        self.expert_selection_pending = False
        self.pending_message = ""
        self.suggested_expert_id = ""
        self.expert_choice = None
        self.pending_user_input = False

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

def detect_expert(message):
    """Detecta el experto basado en palabras clave"""
    if "derecho de petición" in message.lower() or "tutela" in message.lower():
        return "tutela"
    return None

def change_expert(session_state, expert_key, reason="Selección manual"):
    """Cambia el experto actual"""
    print(f"\nCambiando a experto: {expert_key}, Razón: {reason}")
    session_state.current_expert = expert_key
    session_state.expert_history.append({
        "timestamp": datetime.now().strftime("%I:%M:%S %p"),
        "expert": expert_key,
        "reason": reason
    })

def process_message(session_state, message, expert_key):
    """Procesa un mensaje con un experto específico"""
    print(f"\nProcesando mensaje con experto: {expert_key}")
    print(f"Mensaje: '{message}'")
    time.sleep(1)  # Simular tiempo de procesamiento
    
    # Simular respuesta según el experto
    if expert_key == "tutela":
        response = "Como experto en tutelas, te informo que si han pasado más de 90 días sin respuesta a tu derecho de petición, puedes interponer una acción de tutela por violación al derecho fundamental de petición."
    else:
        response = f"Respuesta del experto {expert_key} a tu mensaje."
    
    # Guardar la respuesta
    session_state.messages.append({
        "role": "assistant", 
        "content": response,
        "expert": expert_key
    })
    
    print(f"\nRespuesta: {response}")
    return response

def test_expert_selection_flow():
    """Prueba el flujo de selección de expertos"""
    # Inicializar estado
    session_state = SessionState()
    session_state.expert_history.append({
        "timestamp": datetime.now().strftime("%I:%M:%S %p"),
        "expert": session_state.current_expert,
        "reason": "Inicio de conversación"
    })
    
    print("\n=== PRUEBA 1: SELECCIONAR EXPERTO SUGERIDO ===")
    
    # Paso 1: Usuario envía un mensaje
    user_message = "Envie un derecho de petición y no he recibido respuesta aun despues de mas de 90 días. Que puedo hacer?"
    print(f"\nUsuario: {user_message}")
    session_state.messages.append({"role": "user", "content": user_message})
    
    # Paso 2: Detectar experto sugerido
    suggested_expert = detect_expert(user_message)
    print(f"Experto sugerido: {suggested_expert}")
    
    if suggested_expert and suggested_expert != session_state.current_expert:
        # Verificar que el experto sugerido exista
        if suggested_expert in assistants_config:
            expert_titulo = assistants_config[suggested_expert]["titulo"]
            
            # Paso 3: Mostrar opciones al usuario
            print(f"\nTu mensaje parece relacionado con '{expert_titulo}'. ¿Quieres cambiar de experto?")
            print("1. Usar experto sugerido")
            print("2. Continuar con experto actual")
            
            # Simular que el usuario selecciona "Usar experto sugerido"
            choice = "1"
            print(f"\nUsuario selecciona: {choice}")
            
            if choice == "1":
                # Guardar información para la próxima ejecución
                session_state.expert_selection_pending = True
                session_state.pending_message = user_message
                session_state.suggested_expert_id = suggested_expert
                session_state.expert_choice = "suggested"
                
                print("\n--- Simulando recarga de la página ---")
                
                # Paso 4: En la siguiente ejecución, procesar según la elección
                if session_state.expert_selection_pending and session_state.pending_message == user_message:
                    if session_state.expert_choice == "suggested":
                        # Usar el experto sugerido
                        print(f"\nProcesando mensaje con {assistants_config[session_state.suggested_expert_id]['titulo']}...")
                        change_expert(session_state, session_state.suggested_expert_id, "Cambio automático por palabras clave")
                        response_text = process_message(session_state, user_message, session_state.suggested_expert_id)
                        
                        # Limpiar el estado de selección
                        session_state.expert_selection_pending = False
                        session_state.pending_message = ""
                        session_state.suggested_expert_id = ""
                        session_state.expert_choice = None
                        
                        print("\nEstado final después de seleccionar experto sugerido:")
                        print(f"Experto actual: {session_state.current_expert}")
                        print(f"Historial de expertos: {len(session_state.expert_history)} entradas")
                        print(f"Último experto en historial: {session_state.expert_history[-1]['expert']}")
                        print(f"Mensajes: {len(session_state.messages)} mensajes")
    
    print("\n=== PRUEBA 2: CONTINUAR CON EXPERTO ACTUAL ===")
    
    # Reiniciar estado para la segunda prueba
    session_state = SessionState()
    session_state.expert_history.append({
        "timestamp": datetime.now().strftime("%I:%M:%S %p"),
        "expert": session_state.current_expert,
        "reason": "Inicio de conversación"
    })
    
    # Paso 1: Usuario envía un mensaje
    user_message = "Envie un derecho de petición y no he recibido respuesta aun despues de mas de 90 días. Que puedo hacer?"
    print(f"\nUsuario: {user_message}")
    session_state.messages.append({"role": "user", "content": user_message})
    
    # Paso 2: Detectar experto sugerido
    suggested_expert = detect_expert(user_message)
    print(f"Experto sugerido: {suggested_expert}")
    
    if suggested_expert and suggested_expert != session_state.current_expert:
        # Verificar que el experto sugerido exista
        if suggested_expert in assistants_config:
            expert_titulo = assistants_config[suggested_expert]["titulo"]
            
            # Paso 3: Mostrar opciones al usuario
            print(f"\nTu mensaje parece relacionado con '{expert_titulo}'. ¿Quieres cambiar de experto?")
            print("1. Usar experto sugerido")
            print("2. Continuar con experto actual")
            
            # Simular que el usuario selecciona "Continuar con experto actual"
            choice = "2"
            print(f"\nUsuario selecciona: {choice}")
            
            if choice == "2":
                # Guardar información para la próxima ejecución
                session_state.expert_selection_pending = True
                session_state.pending_message = user_message
                session_state.suggested_expert_id = suggested_expert
                session_state.expert_choice = "current"
                
                print("\n--- Simulando recarga de la página ---")
                
                # Paso 4: En la siguiente ejecución, procesar según la elección
                if session_state.expert_selection_pending and session_state.pending_message == user_message:
                    if session_state.expert_choice == "current":
                        # Continuar con el experto actual
                        print(f"\nProcesando mensaje con {assistants_config[session_state.current_expert]['titulo']}...")
                        response_text = process_message(session_state, user_message, session_state.current_expert)
                        
                        # Limpiar el estado de selección
                        session_state.expert_selection_pending = False
                        session_state.pending_message = ""
                        session_state.suggested_expert_id = ""
                        session_state.expert_choice = None
                        
                        print("\nEstado final después de continuar con experto actual:")
                        print(f"Experto actual: {session_state.current_expert}")
                        print(f"Historial de expertos: {len(session_state.expert_history)} entradas")
                        print(f"Mensajes: {len(session_state.messages)} mensajes")

if __name__ == "__main__":
    test_expert_selection_flow()
