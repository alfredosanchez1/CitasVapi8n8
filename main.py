from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import json
from typing import Optional, Dict, Any
import requests

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="Consultorio Médico Vapi Integration", version="1.0.0")

# Configuración
VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_PHONE_NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
VAPI_ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")

# Configuración Telnyx
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
TELNYX_PHONE_NUMBER = "+526624920537"

# Modelos de datos
class CallRequest(BaseModel):
    phone_number: str
    patient_name: Optional[str] = None
    reason: Optional[str] = None

class VapiWebhook(BaseModel):
    type: str
    call_id: str
    data: Dict[str, Any]

class TelnyxWebhook(BaseModel):
    data: Dict[str, Any]
    meta: Dict[str, Any]

# Base de conocimiento (simplificada)
KNOWLEDGE_BASE = {
    "horarios": "Nuestros horarios son de lunes a viernes de 8:00 a 18:00. Sábados de 9:00 a 14:00.",
    "ubicacion": "Estamos ubicados en [DIRECCIÓN]. Contamos con estacionamiento disponible.",
    "citas": "Para reservar una cita, necesito su nombre, número de teléfono y motivo de consulta.",
    "preparacion": "Para la primera consulta traiga: documento de identidad, carnet de obra social, estudios previos.",
    "emergencias": "Para emergencias médicas, acuda inmediatamente al servicio de urgencias más cercano."
}

@app.get("/")
async def root():
    return {"message": "API del Consultorio Médico - Dr. Xavier Xijemez Xifra - Railway Deploy v1.0"}

@app.get("/test")
async def test():
    """Endpoint de prueba simple"""
    return {"message": "Test endpoint working"}

@app.post("/create-call")
async def create_call(call_request: CallRequest):
    """Crear una llamada usando Vapi"""
    try:
        # Aquí iría la integración real con Vapi
        # Por ahora simulamos la respuesta
        
        call_data = {
            "phone_number": call_request.phone_number,
            "patient_name": call_request.patient_name,
            "reason": call_request.reason,
            "status": "initiated",
            "call_id": f"call_{hash(call_request.phone_number)}"
        }
        
        return {
            "success": True,
            "message": "Llamada iniciada",
            "call_data": call_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/vapi-webhook")
async def vapi_webhook(request: Request):
    """Webhook para recibir eventos de Vapi"""
    try:
        body = await request.json()
        
        # Procesar diferentes tipos de eventos
        event_type = body.get("type")
        
        if event_type == "call-started":
            # Llamada iniciada
            return {"status": "processed", "message": "Call started"}
            
        elif event_type == "call-ended":
            # Llamada terminada
            return {"status": "processed", "message": "Call ended"}
            
        elif event_type == "speech-start":
            # Usuario empezó a hablar
            return {"status": "processed", "message": "Speech started"}
            
        elif event_type == "speech-end":
            # Usuario terminó de hablar
            return {"status": "processed", "message": "Speech ended"}
            
        elif event_type == "function-call":
            # Función llamada por el asistente
            return await handle_function_call(body)
            
        else:
            return {"status": "ignored", "message": f"Unknown event type: {event_type}"}
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def handle_function_call(body: Dict[str, Any]):
    """Manejar llamadas a funciones desde Vapi"""
    function_name = body.get("data", {}).get("name")
    arguments = body.get("data", {}).get("arguments", {})
    
    if function_name == "get_appointment_info":
        return {
            "result": {
                "horarios": KNOWLEDGE_BASE["horarios"],
                "ubicacion": KNOWLEDGE_BASE["ubicacion"],
                "preparacion": KNOWLEDGE_BASE["preparacion"]
            }
        }
    
    elif function_name == "schedule_appointment":
        # Aquí integrarías con 8n8 o tu base de datos
        patient_name = arguments.get("patient_name")
        phone = arguments.get("phone")
        date = arguments.get("date")
        time = arguments.get("time")
        
        # Simular guardado en base de datos
        appointment = {
            "id": f"apt_{hash(phone)}",
            "patient_name": patient_name,
            "phone": phone,
            "date": date,
            "time": time,
            "status": "confirmed"
        }
        
        return {
            "result": {
                "success": True,
                "appointment": appointment,
                "message": f"Cita confirmada para {patient_name} el {date} a las {time}"
            }
        }
    
    return {"result": {"error": "Function not found"}}

@app.get("/appointments")
async def get_appointments():
    """Obtener lista de citas (simulado)"""
    return {
        "appointments": [
            {
                "id": "apt_1",
                "patient_name": "Juan Pérez",
                "phone": "+1234567890",
                "date": "2024-01-15",
                "time": "10:00",
                "status": "confirmed"
            }
        ]
    }

@app.get("/health")
async def health_check():
    """Verificar estado del servidor"""
    return {"status": "healthy"}

@app.post("/telnyx-webhook")
async def telnyx_webhook(request: Request):
    """Webhook para recibir eventos de Telnyx"""
    try:
        body = await request.json()
        print(f"📞 Telnyx webhook recibido: {json.dumps(body, indent=2)}")
        
        # Procesar diferentes tipos de eventos de Telnyx
        event_type = body.get("data", {}).get("event_type")
        print(f"🎯 Evento detectado: {event_type}")
        
        if event_type == "call.initiated":
            # Llamada iniciada
            print("📱 Llamada iniciada")
            return {"status": "processed", "message": "Call initiated"}
            
        elif event_type == "call.answered":
            # Llamada contestada
            print("✅ Llamada contestada")
            return {"status": "processed", "message": "Call answered"}
            
        elif event_type == "call.hangup":
            # Llamada terminada
            print("📴 Llamada terminada")
            return {"status": "processed", "message": "Call ended"}
            
        elif event_type == "call.speech.gathered":
            # Speech reconocido
            speech_text = body.get("data", {}).get("payload", {}).get("speech", "")
            print(f"🎤 Speech reconocido: {speech_text}")
            
            # Aquí procesarías el speech con IA
            response = await process_speech_with_ai(speech_text)
            print(f"🤖 Respuesta IA: {response}")
            
            return {
                "status": "processed", 
                "message": "Speech processed",
                "response": response
            }
            
        else:
            # Para eventos desconocidos o llamadas iniciales, devolver TeXML
            print(f"❓ Evento desconocido o llamada inicial: {event_type}")
            
            # Devolver TeXML simple para manejar la llamada
            texml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">
        Bienvenido al consultorio del Dr. Xavier Xijemez Xifra. 
        Soy su asistente virtual. ¿En qué puedo ayudarle hoy?
        
        Puede decirme si desea:
        - Agendar una cita
        - Consultar horarios
        - Información sobre ubicación
        - O cualquier otra consulta
        
        Por favor, dígame su nombre y el motivo de su consulta.
    </Say>
    <Hangup/>
</Response>"""
            
            return Response(content=texml_response, media_type="application/xml")
            
    except Exception as e:
        print(f"❌ Error en Telnyx webhook: {e}")
        raise HTTPException(status_code=400, detail=str(e))

async def process_speech_with_ai(speech_text: str):
    """Procesar speech con IA para citas médicas"""
    try:
        # Aquí integrarías con OpenAI, Claude, etc.
        # Por ahora simulamos la respuesta
        
        if "cita" in speech_text.lower() or "appointment" in speech_text.lower():
            return {
                "response": "Entiendo que quieres agendar una cita. ¿Podrías decirme tu nombre completo y el motivo de la consulta?",
                "action": "gather_info"
            }
        elif "horarios" in speech_text.lower():
            return {
                "response": "Nuestros horarios son de lunes a viernes de 8:00 a 18:00. Sábados de 9:00 a 14:00.",
                "action": "info"
            }
        else:
            return {
                "response": "Gracias por llamar al consultorio del Dr. Xavier Xijemez Xifra. ¿En qué puedo ayudarte?",
                "action": "general"
            }
    except Exception as e:
        return {
            "response": "Lo siento, no pude procesar tu solicitud. ¿Podrías repetir?",
            "action": "error"
        }

@app.post("/create-telnyx-call")
async def create_telnyx_call(call_request: CallRequest):
    """Crear una llamada usando Telnyx"""
    try:
        # Aquí iría la integración real con Telnyx
        # Por ahora simulamos la respuesta
        
        call_data = {
            "phone_number": call_request.phone_number,
            "patient_name": call_request.patient_name,
            "reason": call_request.reason,
            "status": "initiated",
            "call_id": f"telnyx_call_{hash(call_request.phone_number)}",
            "provider": "telnyx"
        }
        
        return {
            "success": True,
            "message": "Llamada Telnyx iniciada",
            "call_data": call_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 