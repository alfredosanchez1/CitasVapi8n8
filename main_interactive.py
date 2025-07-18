from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
import os
from dotenv import load_dotenv
import json
from typing import Optional, Dict, Any

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="Consultorio Médico - Interactive Version", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "API del Consultorio Médico - Dra. Dolores Remedios del Rincón - Interactive Version"}

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
            # Contenido JSON
            try:
                body = await request.json()
                print(f"📞 Telnyx webhook JSON recibido: {json.dumps(body, indent=2)}")
                return {"status": "processed", "message": "JSON webhook processed"}
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing JSON: {e}")
                return {"status": "error", "message": f"Invalid JSON: {str(e)}"}
        
        elif 'application/x-www-form-urlencoded' in content_type:
            # Contenido form-urlencoded (común en webhooks de telefonía)
            try:
                form_data = await request.form()
                print(f"📞 Telnyx webhook form data recibido: {dict(form_data)}")
                
                # Extraer información de la llamada
                from_number = form_data.get('From', '')
                to_number = form_data.get('To', '')
                call_sid = form_data.get('CallSid', '')
                digits = form_data.get('Digits', '')  # Para DTMF
                
                print(f"📱 Llamada recibida:")
                print(f"   Desde: {from_number}")
                print(f"   Hacia: {to_number}")
                print(f"   CallSid: {call_sid}")
                print(f"   Digits: {digits}")
                
                # Determinar el paso de la conversación
                conversation_step = get_conversation_step(from_number)
                
                if conversation_step == 0:
                    # Primer contacto - dar bienvenida y menú principal
                    return await handle_initial_greeting(from_number, call_sid)
                elif conversation_step == 1:
                    # Usuario seleccionó una opción del menú principal
                    return await handle_main_menu_selection(digits, from_number, call_sid)
                elif conversation_step == 2:
                    # Usuario en submenú específico
                    return await handle_submenu_selection(digits, from_number, call_sid)
                else:
                    # Finalizar conversación
                    return await handle_conversation_end(from_number, call_sid)
                
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

# Almacenamiento simple de contexto de conversación
conversation_contexts = {}

def get_conversation_step(phone_number: str) -> int:
    """Obtener el paso actual de la conversación"""
    if phone_number not in conversation_contexts:
        conversation_contexts[phone_number] = {"step": 0, "data": {}}
    return conversation_contexts[phone_number]["step"]

def update_conversation_step(phone_number: str, step: int, data: Dict = None):
    """Actualizar el paso de la conversación"""
    if phone_number not in conversation_contexts:
        conversation_contexts[phone_number] = {"step": 0, "data": {}}
    conversation_contexts[phone_number]["step"] = step
    if data:
        conversation_contexts[phone_number]["data"].update(data)

async def handle_initial_greeting(phone_number: str, call_sid: str):
    """Manejar el saludo inicial y presentar menú principal"""
    try:
        # Generar saludo personalizado con AI
        from ai_conversation_enhanced import enhanced_ai_manager
        greeting = await enhanced_ai_manager.generate_response(phone_number)
        print(f"🤖 Saludo AI generado: {greeting}")
    except Exception as e:
        print(f"❌ Error con AI manager: {e}")
        greeting = "¡Hola! Bienvenido al Consultorio de la Dra. Dolores Remedios del Rincón, especialista en Medicina Interna."
    
    # Menú principal
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
    
    update_conversation_step(phone_number, 1)
    return Response(content=texml_response, media_type="application/xml")

async def handle_main_menu_selection(digits: str, phone_number: str, call_sid: str):
    """Manejar la selección del menú principal"""
    if digits == "1":
        # Agendar cita
        return await handle_appointment_booking(phone_number, call_sid)
    elif digits == "2":
        # Horarios y ubicación
        return await handle_schedule_info(phone_number, call_sid)
    elif digits == "3":
        # Preparación para consultas
        return await handle_preparation_info(phone_number, call_sid)
    elif digits == "4":
        # Hablar con equipo
        return await handle_team_connection(phone_number, call_sid)
    elif digits == "0":
        # Finalizar
        return await handle_conversation_end(phone_number, call_sid)
    else:
        # Opción inválida
        return await handle_invalid_option(phone_number, call_sid)

async def handle_appointment_booking(phone_number: str, call_sid: str):
    """Manejar el proceso de agendar cita"""
    menu_text = """
    Para agendar su cita, necesito recopilar algunos datos.
    
    Presione 1 si es primera consulta
    Presione 2 si es consulta de seguimiento
    Presione 3 para volver al menú principal
    Presione 0 para finalizar
    """
    
    texml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">
        {menu_text}
    </Say>
    <Gather input="dtmf" timeout="10" numDigits="1" action="https://web-production-a2b02.up.railway.app/telnyx-webhook" method="POST">
        <Say voice="alice" language="es-MX">
            Si no selecciona una opción, volveremos al menú principal.
        </Say>
    </Gather>
    <Say voice="alice" language="es-MX">
        Volviendo al menú principal.
    </Say>
    <Redirect>https://web-production-a2b02.up.railway.app/telnyx-webhook</Redirect>
</Response>"""
    
    update_conversation_step(phone_number, 2, {"action": "appointment_booking"})
    return Response(content=texml_response, media_type="application/xml")

async def handle_schedule_info(phone_number: str, call_sid: str):
    """Proporcionar información de horarios y ubicación"""
    try:
        # Generar respuesta con AI usando knowledge base
        from ai_conversation_enhanced import enhanced_ai_manager
        response = await enhanced_ai_manager.generate_response(phone_number, "Necesito información sobre horarios y ubicación del consultorio")
        print(f"🤖 Respuesta AI para horarios: {response}")
    except Exception as e:
        print(f"❌ Error con AI manager: {e}")
        response = "Nuestros horarios son de lunes a viernes de 8:00 a 18:00. Sábados de 9:00 a 14:00. Estamos ubicados en [DIRECCIÓN]. Contamos con estacionamiento disponible."
    
    menu_text = f"""
    {response}
    
    Presione 1 para volver al menú principal
    Presione 2 para agendar una cita
    Presione 0 para finalizar
    """
    
    texml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">
        {menu_text}
    </Say>
    <Gather input="dtmf" timeout="10" numDigits="1" action="https://web-production-a2b02.up.railway.app/telnyx-webhook" method="POST">
        <Say voice="alice" language="es-MX">
            Si no selecciona una opción, volveremos al menú principal.
        </Say>
    </Gather>
    <Say voice="alice" language="es-MX">
        Volviendo al menú principal.
    </Say>
    <Redirect>https://web-production-a2b02.up.railway.app/telnyx-webhook</Redirect>
</Response>"""
    
    return Response(content=texml_response, media_type="application/xml")

async def handle_preparation_info(phone_number: str, call_sid: str):
    """Proporcionar información sobre preparación para consultas"""
    try:
        # Generar respuesta con AI usando knowledge base
        from ai_conversation_enhanced import enhanced_ai_manager
        response = await enhanced_ai_manager.generate_response(phone_number, "Necesito información sobre qué documentos traer y cómo prepararme para la consulta")
        print(f"🤖 Respuesta AI para preparación: {response}")
    except Exception as e:
        print(f"❌ Error con AI manager: {e}")
        response = "Para la primera consulta traiga: documento de identidad, carnet de obra social, estudios médicos previos, lista de medicamentos actuales y resumen de su historia clínica si tiene."
    
    menu_text = f"""
    {response}
    
    Presione 1 para volver al menú principal
    Presione 2 para agendar una cita
    Presione 0 para finalizar
    """
    
    texml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">
        {menu_text}
    </Say>
    <Gather input="dtmf" timeout="10" numDigits="1" action="https://web-production-a2b02.up.railway.app/telnyx-webhook" method="POST">
        <Say voice="alice" language="es-MX">
            Si no selecciona una opción, volveremos al menú principal.
        </Say>
    </Gather>
    <Say voice="alice" language="es-MX">
        Volviendo al menú principal.
    </Say>
    <Redirect>https://web-production-a2b02.up.railway.app/telnyx-webhook</Redirect>
</Response>"""
    
    return Response(content=texml_response, media_type="application/xml")

async def handle_team_connection(phone_number: str, call_sid: str):
    """Conectar con miembro del equipo"""
    texml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">
        Un miembro de nuestro equipo se pondrá en contacto con usted pronto. Gracias por su paciencia.
    </Say>
    <Hangup/>
</Response>"""
    
    update_conversation_step(phone_number, 0)  # Reset conversation
    return Response(content=texml_response, media_type="application/xml")

async def handle_conversation_end(phone_number: str, call_sid: str):
    """Finalizar la conversación"""
    texml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">
        Gracias por llamar al Consultorio de la Dra. Dolores Remedios del Rincón. Que tenga un excelente día.
    </Say>
    <Hangup/>
</Response>"""
    
    update_conversation_step(phone_number, 0)  # Reset conversation
    return Response(content=texml_response, media_type="application/xml")

async def handle_invalid_option(phone_number: str, call_sid: str):
    """Manejar opción inválida"""
    texml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">
        Opción no válida. Volviendo al menú principal.
    </Say>
    <Redirect>https://web-production-a2b02.up.railway.app/telnyx-webhook</Redirect>
</Response>"""
    
    return Response(content=texml_response, media_type="application/xml")

async def handle_submenu_selection(digits: str, phone_number: str, call_sid: str):
    """Manejar selección de submenú"""
    # Por ahora, redirigir al menú principal
    return await handle_invalid_option(phone_number, call_sid)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 