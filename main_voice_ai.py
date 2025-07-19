from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
import os
from dotenv import load_dotenv
import json
from typing import Optional, Dict, Any
import asyncio
import aiohttp

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="Consultorio Médico - Voice AI Bot", version="1.0.0")

# Configuración de Telnyx
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
TELNYX_WEBHOOK_SECRET = os.getenv("TELNYX_WEBHOOK_SECRET", "your_webhook_secret")

@app.get("/")
async def root():
    return {"message": "API del Consultorio Médico - Dra. Dolores Remedios del Rincón - Voice AI Bot"}

@app.get("/health")
async def health_check():
    """Endpoint de health check para Railway"""
    return {"status": "healthy", "message": "Server is running"}

@app.get("/test")
async def test():
    """Endpoint de prueba simple"""
    return {"message": "Test endpoint working"}

@app.post("/telnyx-webhook")
async def telnyx_webhook(request: Request):
    """Webhook para recibir eventos de Telnyx Voice API"""
    try:
        # Obtener el contenido raw del request para debugging
        raw_body = await request.body()
        print(f"📞 Raw body recibido: {raw_body}")
        print(f"📞 Content-Type: {request.headers.get('content-type', 'No content-type')}")
        
        # Verificar si el body está vacío
        if not raw_body:
            print("❌ Body vacío recibido")
            return {"status": "error", "message": "Empty body received"}
        
        content_type = request.headers.get('content-type', '').lower()
        
        # Manejar diferentes tipos de contenido
        if 'application/json' in content_type:
            # Contenido JSON - Eventos de Telnyx Voice API
            try:
                body = await request.json()
                print(f"📞 Telnyx Voice API event recibido: {json.dumps(body, indent=2)}")
                
                # Procesar evento de Telnyx Voice API
                return await handle_voice_api_event(body)
                
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing JSON: {e}")
                return {"status": "error", "message": f"Invalid JSON: {str(e)}"}
        
        elif 'application/x-www-form-urlencoded' in content_type:
            # Contenido form-urlencoded - Webhooks tradicionales
            try:
                form_data = await request.form()
                print(f"📞 Telnyx webhook form data recibido: {dict(form_data)}")
                
                # Extraer información de la llamada
                from_number = form_data.get('From', '')
                to_number = form_data.get('To', '')
                call_sid = form_data.get('CallSid', '')
                digits = form_data.get('Digits', '')
                
                print(f"📱 Llamada recibida:")
                print(f"   Desde: {from_number}")
                print(f"   Hacia: {to_number}")
                print(f"   CallSid: {call_sid}")
                print(f"   Digits: {digits}")
                
                # Para webhooks tradicionales, usar menú DTMF
                return await handle_dtmf_menu(from_number, call_sid, digits)
                
            except Exception as e:
                print(f"❌ Error parsing form data: {e}")
                return {"status": "error", "message": f"Invalid form data: {str(e)}"}
        
        else:
            # Intentar parsear como texto plano
            try:
                text_content = raw_body.decode('utf-8')
                print(f"📞 Telnyx webhook text recibido: {text_content}")
                return {"status": "processed", "message": "Text webhook processed"}
            except Exception as e:
                print(f"❌ Error parsing text content: {e}")
                return {"status": "error", "message": f"Invalid text content: {str(e)}"}
        
    except Exception as e:
        print(f"❌ Error general en webhook: {e}")
        return {"status": "error", "message": str(e)}

async def handle_voice_api_event(event_data: Dict):
    """Manejar eventos de Telnyx Voice API"""
    event_type = event_data.get('event_type', '')
    
    print(f"🎯 Procesando evento: {event_type}")
    
    if event_type == 'call.initiated':
        # Llamada iniciada - configurar para reconocimiento de voz
        return await handle_call_initiated(event_data)
    
    elif event_type == 'call.answered':
        # Llamada contestada - comenzar conversación
        return await handle_call_answered(event_data)
    
    elif event_type == 'call.speech.gathered':
        # Voz reconocida - procesar con AI
        return await handle_speech_gathered(event_data)
    
    elif event_type == 'call.hangup':
        # Llamada terminada
        return await handle_call_hangup(event_data)
    
    else:
        # Otros eventos
        print(f"📝 Evento no manejado: {event_type}")
        return {"status": "processed", "message": f"Event {event_type} processed"}

async def handle_call_initiated(event_data: Dict):
    """Manejar llamada iniciada"""
    call_control_id = event_data.get('data', {}).get('call_control_id')
    
    if call_control_id:
        # Configurar la llamada para reconocimiento de voz
        await configure_voice_recognition(call_control_id)
    
    return {"status": "processed", "message": "Call initiated"}

async def handle_call_answered(event_data: Dict):
    """Manejar llamada contestada"""
    call_control_id = event_data.get('data', {}).get('call_control_id')
    
    if call_control_id:
        # Comenzar conversación con saludo
        await start_conversation(call_control_id)
    
    return {"status": "processed", "message": "Call answered"}

async def handle_speech_gathered(event_data: Dict):
    """Manejar voz reconocida"""
    call_control_id = event_data.get('data', {}).get('call_control_id')
    speech = event_data.get('data', {}).get('payload', {}).get('speech', {}).get('text', '')
    
    print(f"🎤 Voz reconocida: {speech}")
    
    if call_control_id and speech:
        # Procesar con AI y responder
        await process_speech_with_ai(call_control_id, speech)
    
    return {"status": "processed", "message": "Speech processed"}

async def handle_call_hangup(event_data: Dict):
    """Manejar llamada terminada"""
    call_control_id = event_data.get('data', {}).get('call_control_id')
    
    print(f"📞 Llamada terminada: {call_control_id}")
    
    return {"status": "processed", "message": "Call ended"}

async def configure_voice_recognition(call_control_id: str):
    """Configurar reconocimiento de voz en la llamada"""
    url = f"https://api.telnyx.com/v2/calls/{call_control_id}/actions"
    
    headers = {
        "Authorization": f"Bearer {TELNYX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Configurar para reconocimiento de voz
    payload = {
        "speech": {
            "language": "es-MX",
            "interim_results": False,
            "end_of_speech_detection": True
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                print(f"🎤 Configuración de voz: {response.status}")
                return await response.json()
    except Exception as e:
        print(f"❌ Error configurando voz: {e}")

async def start_conversation(call_control_id: str):
    """Comenzar conversación con saludo"""
    try:
        # Generar saludo con AI
        from ai_conversation_enhanced import enhanced_ai_manager
        greeting = await enhanced_ai_manager.generate_response("+1234567890")  # Número dummy
        print(f"🤖 Saludo AI generado: {greeting}")
    except Exception as e:
        print(f"❌ Error con AI manager: {e}")
        greeting = "¡Hola! Bienvenido al Consultorio de la Dra. Dolores Remedios del Rincón. Soy su asistente virtual. ¿En qué puedo ayudarle hoy?"
    
    await speak_text(call_control_id, greeting)
    await start_listening(call_control_id)

async def process_speech_with_ai(call_control_id: str, speech: str):
    """Procesar voz con AI y responder"""
    try:
        # Generar respuesta con AI
        from ai_conversation_enhanced import enhanced_ai_manager
        response = await enhanced_ai_manager.generate_response("+1234567890", speech)
        print(f"🤖 Respuesta AI: {response}")
    except Exception as e:
        print(f"❌ Error con AI manager: {e}")
        response = "Entiendo su consulta. Un miembro de nuestro equipo se pondrá en contacto con usted pronto."
    
    await speak_text(call_control_id, response)
    await start_listening(call_control_id)

async def speak_text(call_control_id: str, text: str):
    """Hacer que el sistema hable el texto"""
    url = f"https://api.telnyx.com/v2/calls/{call_control_id}/actions"
    
    headers = {
        "Authorization": f"Bearer {TELNYX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "speak": {
            "payload": text,
            "voice": "alice",
            "language": "es-MX"
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                print(f"🗣️ Speak response: {response.status}")
                return await response.json()
    except Exception as e:
        print(f"❌ Error hablando: {e}")

async def start_listening(call_control_id: str):
    """Comenzar a escuchar voz del usuario"""
    url = f"https://api.telnyx.com/v2/calls/{call_control_id}/actions"
    
    headers = {
        "Authorization": f"Bearer {TELNYX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "gather_using_speak": {
            "speech": {
                "language": "es-MX",
                "interim_results": False,
                "end_of_speech_detection": True
            },
            "speak": {
                "payload": "Estoy escuchando...",
                "voice": "alice",
                "language": "es-MX"
            }
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                print(f"👂 Listen response: {response.status}")
                return await response.json()
    except Exception as e:
        print(f"❌ Error escuchando: {e}")

# Para webhooks tradicionales (DTMF)
async def handle_dtmf_menu(from_number: str, call_sid: str, digits: str):
    """Manejar menú DTMF para webhooks tradicionales"""
    if not digits:
        # Primer contacto - dar bienvenida y menú
        return await handle_initial_greeting_dtmf(from_number, call_sid)
    else:
        # Usuario seleccionó opción
        return await handle_menu_selection_dtmf(digits, from_number, call_sid)

async def handle_initial_greeting_dtmf(from_number: str, call_sid: str):
    """Saludo inicial con menú DTMF"""
    try:
        from ai_conversation_enhanced import enhanced_ai_manager
        greeting = await enhanced_ai_manager.generate_response(from_number)
        print(f"🤖 Saludo AI generado: {greeting}")
    except Exception as e:
        print(f"❌ Error con AI manager: {e}")
        greeting = "¡Hola! Bienvenido al Consultorio de la Dra. Dolores Remedios del Rincón."
    
    menu_text = f"""
    {greeting}
    
    Por favor, seleccione una opción:
    
    Presione 1 para agendar una cita
    Presione 2 para consultar horarios y ubicación
    Presione 3 para información sobre preparación para consultas
    Presione 4 para hablar con un miembro del equipo
    Presione 0 para finalizar la llamada
    """
    
    texml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">
        {menu_text}
    </Say>
    <Gather input="dtmf" timeout="10" numDigits="1" action="https://web-production-a2b02.up.railway.app/telnyx-webhook" method="POST">
        <Say voice="alice" language="es-MX">
            Si no selecciona una opción, lo conectaremos con un miembro del equipo.
        </Say>
    </Gather>
    <Say voice="alice" language="es-MX">
        Conectándolo con un miembro del equipo. Gracias por llamar.
    </Say>
    <Hangup/>
</Response>"""
    
    return Response(content=texml_response, media_type="application/xml")

async def handle_menu_selection_dtmf(digits: str, from_number: str, call_sid: str):
    """Manejar selección de menú DTMF"""
    if digits == "1":
        response = "Para agendar su cita, necesito recopilar algunos datos. Un miembro de nuestro equipo se pondrá en contacto con usted pronto."
    elif digits == "2":
        response = "Nuestros horarios son de lunes a viernes de 8:00 a 18:00. Sábados de 9:00 a 14:00. Estamos ubicados en [DIRECCIÓN]."
    elif digits == "3":
        response = "Para la primera consulta traiga: documento de identidad, carnet de obra social, estudios médicos previos y lista de medicamentos actuales."
    elif digits == "4":
        response = "Un miembro de nuestro equipo se pondrá en contacto con usted pronto. Gracias por su paciencia."
    elif digits == "0":
        response = "Gracias por llamar al Consultorio de la Dra. Dolores Remedios del Rincón. Que tenga un excelente día."
    else:
        response = "Opción no válida. Un miembro de nuestro equipo se pondrá en contacto con usted pronto."
    
    texml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">
        {response}
    </Say>
    <Hangup/>
</Response>"""
    
    return Response(content=texml_response, media_type="application/xml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 