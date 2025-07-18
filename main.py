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
            # Contenido JSON
            try:
                body = await request.json()
                print(f"📞 Telnyx webhook JSON recibido: {json.dumps(body, indent=2)}")
                return await process_telnyx_json_webhook(body)
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing JSON: {e}")
                return {"status": "error", "message": f"Invalid JSON: {str(e)}"}
        
        elif 'application/x-www-form-urlencoded' in content_type:
            # Contenido form-urlencoded (común en webhooks de telefonía)
            try:
                form_data = await request.form()
                print(f"📞 Telnyx webhook form data recibido: {dict(form_data)}")
                return await process_telnyx_form_webhook(form_data)
            except Exception as e:
                print(f"❌ Error parsing form data: {e}")
                return {"status": "error", "message": f"Invalid form data: {str(e)}"}
        
        else:
            # Intentar parsear como texto plano
            try:
                text_content = raw_body.decode('utf-8')
                print(f"📞 Telnyx webhook text recibido: {text_content}")
                return await process_telnyx_text_webhook(text_content)
            except Exception as e:
                print(f"❌ Error parsing text content: {e}")
                return {"status": "error", "message": f"Invalid text content: {str(e)}"}
        
    except Exception as e:
        print(f"❌ Error general en webhook: {e}")
        return {"status": "error", "message": str(e)}

async def process_telnyx_form_webhook(form_data):
    """Procesar webhook de Telnyx en formato form-urlencoded"""
    try:
        # Extraer información de la llamada
        from_number = form_data.get('From', '')
        to_number = form_data.get('To', '')
        call_sid = form_data.get('CallSid', '')
        caller_id = form_data.get('CallerId', '')
        
        print(f"📱 Llamada recibida:")
        print(f"   Desde: {from_number}")
        print(f"   Hacia: {to_number}")
        print(f"   CallSid: {call_sid}")
        print(f"   CallerId: {caller_id}")
        
        # Usar Telnyx AI para conversación interactiva
        texml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <AI>
        <Prompt>
            Eres una asistente virtual del consultorio médico del Dr. Xavier Xijemez Xifra. 
            Tu objetivo es ayudar a los pacientes a agendar citas y responder sus consultas.
            
            Información del consultorio:
            - Horarios: Lunes a viernes de 8:00 a 18:00, Sábados de 9:00 a 14:00
            - Ubicación: [DIRECCIÓN DEL CONSULTORIO]
            - Para primera consulta: traer documento de identidad, carnet de obra social, estudios previos
            - Emergencias: acudir al servicio de urgencias más cercano
            
            Instrucciones:
            1. Saluda amablemente al paciente
            2. Pregunta en qué puedes ayudarle
            3. Si quiere agendar cita: recopila nombre, teléfono, motivo de consulta
            4. Si pregunta por horarios, ubicación, etc.: proporciona la información
            5. Sé profesional pero cálida
            6. Habla en español mexicano
            7. Confirma la información antes de terminar la llamada
        </Prompt>
        <Voice>alice</Voice>
        <Language>es-MX</Language>
        <InterruptionThreshold>0.5</InterruptionThreshold>
        <PostUtteranceSilence>1000</PostUtteranceSilence>
        <WebhookUrl>https://tu-railway-app.railway.app/telnyx-ai-webhook</WebhookUrl>
    </AI>
</Response>"""
        
        return Response(content=texml_response, media_type="application/xml")
        
    except Exception as e:
        print(f"❌ Error procesando form webhook: {e}")
        return {"status": "error", "message": str(e)}

async def process_telnyx_json_webhook(body):
    """Procesar webhook de Telnyx en formato JSON"""
    try:
        event_type = body.get("data", {}).get("event_type")
        print(f"🎯 Evento JSON detectado: {event_type}")
        
        if event_type == "call.initiated":
            print("📱 Llamada iniciada")
            return {"status": "processed", "message": "Call initiated"}
            
        elif event_type == "call.answered":
            print("✅ Llamada contestada")
            return {"status": "processed", "message": "Call answered"}
            
        elif event_type == "call.hangup":
            print("📴 Llamada terminada")
            return {"status": "processed", "message": "Call ended"}
        
        return {"status": "ignored", "message": f"Unknown event type: {event_type}"}
        
    except Exception as e:
        print(f"❌ Error procesando JSON webhook: {e}")
        return {"status": "error", "message": str(e)}

async def process_telnyx_text_webhook(text_content):
    """Procesar webhook de Telnyx en formato texto plano"""
    try:
        print(f"📝 Procesando contenido de texto: {text_content}")
        return {"status": "processed", "message": "Text content processed"}
        
    except Exception as e:
        print(f"❌ Error procesando text webhook: {e}")
        return {"status": "error", "message": str(e)}

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

@app.post("/telnyx-ai-webhook")
async def telnyx_ai_webhook(request: Request):
    """Webhook para recibir eventos de Telnyx AI"""
    try:
        body = await request.json()
        print(f"🤖 Telnyx AI webhook recibido: {json.dumps(body, indent=2)}")
        
        # Procesar diferentes tipos de eventos de Telnyx AI
        event_type = body.get("event_type")
        
        if event_type == "ai.conversation.started":
            print("🤖 Conversación AI iniciada")
            return {"status": "processed", "message": "AI conversation started"}
            
        elif event_type == "ai.conversation.ended":
            print("🤖 Conversación AI terminada")
            return {"status": "processed", "message": "AI conversation ended"}
            
        elif event_type == "ai.speech.recognized":
            # Speech reconocido por la IA
            speech_text = body.get("payload", {}).get("text", "")
            print(f"🎤 Speech reconocido: {speech_text}")
            
            # Aquí puedes procesar el speech y tomar acciones específicas
            # Por ejemplo, guardar información de la cita
            return await process_ai_speech(speech_text, body)
            
        elif event_type == "ai.intent.detected":
            # Intención detectada por la IA
            intent = body.get("payload", {}).get("intent", "")
            print(f"🎯 Intención detectada: {intent}")
            
            return {"status": "processed", "message": f"Intent detected: {intent}"}
        
        return {"status": "ignored", "message": f"Unknown event type: {event_type}"}
        
    except Exception as e:
        print(f"❌ Error en Telnyx AI webhook: {e}")
        return {"status": "error", "message": str(e)}

async def process_ai_speech(speech_text: str, webhook_data: Dict[str, Any]):
    """Procesar speech reconocido por Telnyx AI"""
    try:
        # Extraer información de la llamada
        call_sid = webhook_data.get("call_sid", "")
        from_number = webhook_data.get("from", "")
        
        print(f"📝 Procesando speech: '{speech_text}'")
        print(f"📞 Desde: {from_number}")
        print(f"🆔 CallSid: {call_sid}")
        
        # Aquí puedes implementar lógica específica basada en el contenido del speech
        # Por ejemplo, detectar si el usuario está agendando una cita
        
        if any(word in speech_text.lower() for word in ["cita", "appointment", "agendar", "reservar"]):
            print("📅 Usuario quiere agendar cita")
            # Aquí podrías guardar en base de datos o enviar a 8n8
            
        elif any(word in speech_text.lower() for word in ["horarios", "horario", "schedule"]):
            print("🕐 Usuario pregunta por horarios")
            
        elif any(word in speech_text.lower() for word in ["ubicación", "dirección", "location"]):
            print("📍 Usuario pregunta por ubicación")
        
        return {
            "status": "processed",
            "message": "Speech processed successfully",
            "data": {
                "speech": speech_text,
                "call_sid": call_sid,
                "from": from_number
            }
        }
        
    except Exception as e:
        print(f"❌ Error procesando AI speech: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 