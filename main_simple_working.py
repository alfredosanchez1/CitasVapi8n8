from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
import os
from dotenv import load_dotenv
import json
from typing import Optional, Dict, Any

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="Consultorio Médico - Simple Working Version", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "API del Consultorio Médico - Dra. Dolores Remedios del Rincón - Simple Working Version"}

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
        return {"status": "processed", "message": "Call initiated"}
    
    elif event_type == 'call.answered':
        return {"status": "processed", "message": "Call answered"}
    
    elif event_type == 'call.speech.gathered':
        return {"status": "processed", "message": "Speech processed"}
    
    elif event_type == 'call.hangup':
        return {"status": "processed", "message": "Call ended"}
    
    else:
        print(f"📝 Evento no manejado: {event_type}")
        return {"status": "processed", "message": f"Event {event_type} processed"}

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
    """Saludo inicial con Karla"""
    try:
        # Usar Karla como asistente virtual
        from karla_assistant import karla_assistant
        greeting = await karla_assistant.generate_response(from_number)
        print(f"🤖 Saludo de Karla generado: {greeting}")
    except Exception as e:
        print(f"❌ Error con Karla: {e}")
        greeting = "Hola soy Karla, asistente de la doctora Dolores Remedios del Rincón. ¿En qué puedo ayudarte hoy?"
    
    menu_text = f"""
    {greeting}
    
    Por favor, seleccione una opción:
    
    Presione 1 para agendar una cita nueva
    Presione 2 para cambiar o cancelar una cita existente
    Presione 3 para consultar horarios y ubicación
    Presione 4 para información sobre preparación para consultas
    Presione 5 para hablar con un miembro del equipo
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
    """Manejar selección de menú DTMF con Karla"""
    try:
        from karla_assistant import karla_assistant
        
        if digits == "1":
            response = await karla_assistant.generate_response(from_number, "Necesito agendar una cita nueva")
        elif digits == "2":
            response = await karla_assistant.generate_response(from_number, "Necesito cambiar o cancelar una cita existente")
        elif digits == "3":
            response = await karla_assistant.generate_response(from_number, "Necesito consultar horarios y ubicación")
        elif digits == "4":
            response = await karla_assistant.generate_response(from_number, "Necesito información sobre preparación para consultas")
        elif digits == "5":
            response = "Un miembro de nuestro equipo se pondrá en contacto con usted pronto. Gracias por su paciencia."
        elif digits == "0":
            response = "Gracias por llamar al Consultorio de la Dra. Dolores Remedios del Rincón. Que tenga un excelente día."
        else:
            response = "Opción no válida. Un miembro de nuestro equipo se pondrá en contacto con usted pronto."
            
    except Exception as e:
        print(f"❌ Error con Karla en menú: {e}")
        # Respuestas de fallback
        if digits == "1":
            response = "Para agendar su cita, necesito recopilar algunos datos. Un miembro de nuestro equipo se pondrá en contacto con usted pronto."
        elif digits == "2":
            response = "Para cambiar o cancelar su cita, un miembro de nuestro equipo se pondrá en contacto con usted pronto."
        elif digits == "3":
            response = "Nuestros horarios son de lunes a viernes de 8:00 a 18:00. Sábados de 9:00 a 14:00. Estamos ubicados en [DIRECCIÓN]."
        elif digits == "4":
            response = "Para la primera consulta traiga: documento de identidad, carnet de obra social, estudios médicos previos y lista de medicamentos actuales."
        elif digits == "5":
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