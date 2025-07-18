from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
import os
from dotenv import load_dotenv
import json
from typing import Optional, Dict, Any

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="Consultorio Médico - Simple Version", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "API del Consultorio Médico - Dr. Xavier Xijemez Xifra - Simple Version"}

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
                
                print(f"📱 Llamada recibida:")
                print(f"   Desde: {from_number}")
                print(f"   Hacia: {to_number}")
                print(f"   CallSid: {call_sid}")
                
                # Respuesta simple de TeXML
                texml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">
        ¡Hola! Bienvenido al Consultorio del Dr. Xavier Xijemez Xifra. Un miembro de nuestro equipo se pondrá en contacto con usted pronto. Gracias por llamar.
    </Say>
    <Hangup/>
</Response>"""
                
                return Response(content=texml_response, media_type="application/xml")
                
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 