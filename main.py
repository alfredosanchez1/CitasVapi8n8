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
        
        # Usar Gather con DTMF para conversación interactiva (compatible con trial)
        texml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">
        Bienvenido al consultorio del Dr. Xavier Xijemez Xifra. 
        Soy su asistente virtual. 
        
        Gracias por llamar. Un miembro de nuestro equipo 
        se pondrá en contacto con usted pronto.
    </Say>
    
    <Hangup/>
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

@app.post("/process-speech")
async def process_speech(request: Request):
    """Procesar speech reconocido por Telnyx Gather"""
    try:
        print(f"🎤 Procesando speech request...")
        
        # Obtener parámetros de la URL
        call_sid = request.query_params.get("call_sid", "")
        from_number = request.query_params.get("from", "")
        
        print(f"📞 Parámetros: call_sid={call_sid}, from={from_number}")
        
        # Obtener datos del formulario
        form_data = await request.form()
        print(f"📝 Form data keys: {list(form_data.keys())}")
        
        speech_result = form_data.get("SpeechResult", "")
        confidence = form_data.get("Confidence", "0")
        
        print(f"🎤 Speech procesado:")
        print(f"   Texto: {speech_result}")
        print(f"   Confianza: {confidence}")
        print(f"   CallSid: {call_sid}")
        print(f"   Desde: {from_number}")
        
        # Si no hay speech, dar una respuesta por defecto
        if not speech_result:
            response_text = """No pude escuchar su respuesta claramente. 
            Por favor, dígame en qué puedo ayudarle: 
            si desea agendar una cita, consultar horarios, 
            o información sobre ubicación."""
        else:
            # Procesar el speech con lógica de conversación
            response_text = await generate_conversation_response(speech_result, call_sid, from_number)
        
        # Devolver TeXML con la respuesta
        texml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">
        {response_text}
    </Say>
    
    <Gather 
        input="speech" 
        timeout="10" 
        speechTimeout="auto"
        language="es-MX"
        action="https://web-production-a2b02.up.railway.app/process-speech?call_sid={call_sid}&from={from_number}"
        method="POST">
        
        <Say voice="alice" language="es-MX">
            ¿Hay algo más en lo que pueda ayudarle?
        </Say>
    </Gather>
    
    <Say voice="alice" language="es-MX">
        Gracias por llamar al consultorio del Dr. Xavier Xijemez Xifra. 
        Que tenga un excelente día.
    </Say>
    
    <Hangup/>
</Response>"""
        
        print(f"✅ Respuesta TeXML generada exitosamente")
        return Response(content=texml_response, media_type="application/xml")
        
    except Exception as e:
        print(f"❌ Error procesando speech: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        
        # Devolver respuesta de error simple
        error_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">
        Lo siento, hubo un error procesando su solicitud. 
        Por favor, llame nuevamente.
    </Say>
    <Hangup/>
</Response>"""
        return Response(content=error_response, media_type="application/xml")

@app.post("/process-dtmf")
async def process_dtmf(request: Request):
    """Procesar DTMF (teclas presionadas) de Telnyx Gather"""
    try:
        print(f"🔢 Procesando DTMF request...")
        
        # Obtener parámetros de la URL
        call_sid = request.query_params.get("call_sid", "")
        from_number = request.query_params.get("from", "")
        
        print(f"📞 Parámetros: call_sid={call_sid}, from={from_number}")
        
        # Obtener datos del formulario
        form_data = await request.form()
        print(f"📝 Form data keys: {list(form_data.keys())}")
        
        digits = form_data.get("Digits", "")
        
        print(f"🔢 Dígito presionado: {digits}")
        
        # Procesar la selección del usuario
        response_text = await handle_dtmf_selection(digits, call_sid, from_number)
        
        # Devolver TeXML con la respuesta
        texml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">
        {response_text}
    </Say>
    
    <Gather 
        input="dtmf" 
        timeout="10" 
        numDigits="1"
        action="https://web-production-a2b02.up.railway.app/process-dtmf?call_sid={call_sid}&from={from_number}"
        method="POST">
        
        <Say voice="alice" language="es-MX">
            Para continuar, presione:
            1 - Para agendar una cita
            2 - Para consultar horarios
            3 - Para información sobre ubicación
            4 - Para información sobre preparación
            5 - Para hablar con un operador
            0 - Para terminar la llamada
        </Say>
    </Gather>
    
    <Say voice="alice" language="es-MX">
        Gracias por llamar al consultorio del Dr. Xavier Xijemez Xifra. 
        Que tenga un excelente día.
    </Say>
    
    <Hangup/>
</Response>"""
        
        print(f"✅ Respuesta TeXML generada exitosamente")
        return Response(content=texml_response, media_type="application/xml")
        
    except Exception as e:
        print(f"❌ Error procesando DTMF: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        
        # Devolver respuesta de error simple
        error_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">
        Lo siento, hubo un error procesando su selección. 
        Por favor, llame nuevamente.
    </Say>
    <Hangup/>
</Response>"""
        return Response(content=error_response, media_type="application/xml")

async def handle_dtmf_selection(digits: str, call_sid: str, from_number: str):
    """Manejar selección DTMF del usuario"""
    try:
        print(f"🔢 Procesando selección: {digits}")
        
        if digits == "1":
            return await handle_appointment_dtmf(call_sid, from_number)
        elif digits == "2":
            return handle_schedule_inquiry()
        elif digits == "3":
            return handle_location_inquiry()
        elif digits == "4":
            return handle_preparation_inquiry()
        elif digits == "5":
            return handle_operator_request()
        elif digits == "0":
            return "Gracias por llamar. Que tenga un excelente día."
        else:
            return "Opción no válida. Por favor, seleccione una opción del 1 al 5."
            
    except Exception as e:
        print(f"❌ Error procesando selección DTMF: {e}")
        return "Lo siento, hubo un error procesando su selección."

async def handle_appointment_dtmf(call_sid: str, from_number: str):
    """Manejar solicitud de cita por DTMF"""
    print(f"📅 Usuario seleccionó agendar cita")
    return """Para agendar una cita, necesito recopilar su información.
    
    Por favor, tenga a mano:
    - Su nombre completo
    - Número de teléfono
    - Motivo de la consulta
    
    Un miembro de nuestro equipo se pondrá en contacto con usted 
    para confirmar los detalles y la fecha disponible."""

def handle_operator_request():
    """Manejar solicitud de operador"""
    return """Entiendo que desea hablar con un operador.
    Por favor, espere un momento mientras lo conecto.
    Si no hay operadores disponibles, le devolveremos la llamada."""

async def generate_conversation_response(speech_text: str, call_sid: str, from_number: str):
    """Generar respuesta conversacional basada en el speech del usuario"""
    try:
        speech_lower = speech_text.lower()
        
        # Detectar intenciones del usuario
        if any(word in speech_lower for word in ["cita", "appointment", "agendar", "reservar", "citar"]):
            return await handle_appointment_request(speech_text, call_sid, from_number)
            
        elif any(word in speech_lower for word in ["horarios", "horario", "schedule", "cuándo", "cuando"]):
            return handle_schedule_inquiry()
            
        elif any(word in speech_lower for word in ["ubicación", "dirección", "location", "dónde", "donde"]):
            return handle_location_inquiry()
            
        elif any(word in speech_lower for word in ["preparación", "preparar", "traer", "documentos"]):
            return handle_preparation_inquiry()
            
        elif any(word in speech_lower for word in ["emergencia", "emergencias", "urgencia"]):
            return handle_emergency_inquiry()
            
        else:
            return handle_general_inquiry(speech_text)
            
    except Exception as e:
        print(f"❌ Error generando respuesta: {e}")
        return "Lo siento, no pude procesar su solicitud. ¿Podrías repetir?"

async def handle_appointment_request(speech_text: str, call_sid: str, from_number: str):
    """Manejar solicitud de cita (mantener para compatibilidad)"""
    print(f"📅 Usuario quiere agendar cita: {speech_text}")
    
    if "nombre" in speech_text.lower() and "motivo" in speech_text.lower():
        return """Perfecto, he tomado nota de su información para la cita. 
        Un miembro de nuestro equipo se pondrá en contacto con usted 
        para confirmar los detalles y la fecha disponible. 
        ¿Hay algo más en lo que pueda ayudarle?"""
    else:
        return """Entiendo que quiere agendar una cita. 
        Para ayudarle mejor, necesito saber su nombre completo 
        y el motivo de la consulta. ¿Podría proporcionarme esta información?"""

def handle_schedule_inquiry():
    """Manejar consulta sobre horarios"""
    return """Nuestros horarios de atención son:
    Lunes a viernes de 8:00 de la mañana a 6:00 de la tarde.
    Sábados de 9:00 de la mañana a 2:00 de la tarde.
    Los domingos no atendemos.
    ¿En qué horario le gustaría agendar su cita?"""

def handle_location_inquiry():
    """Manejar consulta sobre ubicación"""
    return """Nos encontramos ubicados en [DIRECCIÓN DEL CONSULTORIO]. 
    Contamos con estacionamiento disponible para nuestros pacientes. 
    ¿Necesita indicaciones para llegar?"""

def handle_preparation_inquiry():
    """Manejar consulta sobre preparación"""
    return """Para su primera consulta, por favor traiga:
    - Documento de identidad
    - Carnet de obra social si tiene
    - Estudios previos si los tiene
    - Lista de medicamentos que toma actualmente"""

def handle_emergency_inquiry():
    """Manejar consulta sobre emergencias"""
    return """Para emergencias médicas, por favor acuda inmediatamente 
    al servicio de urgencias más cercano o llame al 911. 
    No podemos atender emergencias en el consultorio."""

def handle_general_inquiry(speech_text: str):
    """Manejar consultas generales"""
    return f"""Gracias por su consulta. Soy la asistente virtual del 
    Dr. Xavier Xijemez Xifra. Puedo ayudarle con:
    - Agendar citas
    - Consultar horarios
    - Información sobre ubicación
    - Preparación para la consulta
    ¿En cuál de estos temas puedo ayudarle?"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 