"""
Ejemplo de cómo integrar Vapi con tu API FastAPI existente en Render
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_vapi_integration import add_vapi_routes
import os

# Tu aplicación FastAPI existente
app = FastAPI(
    title="Consultorio Médico API",
    description="API para el consultorio del Dr. Xavier Xijemez Xifra con integración Vapi",
    version="1.0.0"
)

# Configurar CORS (si lo necesitas)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configura según tus necesidades
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AÑADIR AQUÍ: Integración con Vapi
add_vapi_routes(app)

# Tus rutas existentes (ejemplos)
@app.get("/")
async def root():
    return {
        "message": "API del Consultorio Médico - Dr. Xavier Xijemez Xifra",
        "version": "1.0.0",
        "integrations": ["Vapi", "8n8 (opcional)"]
    }

@app.get("/api/info")
async def get_api_info():
    """Información de tu API existente"""
    return {
        "name": "Consultorio Médico API",
        "doctor": "Dr. Xavier Xijemez Xifra",
        "specialty": "Medicina Interna",
        "features": [
            "Reserva de citas",
            "Llamadas de voz con Vapi",
            "Gestión de pacientes",
            "Integración con 8n8"
        ]
    }

# Ejemplo de ruta existente que podrías tener
@app.get("/api/patients")
async def get_patients():
    """Obtener lista de pacientes (ejemplo)"""
    return {
        "patients": [
            {
                "id": "1",
                "name": "Juan Pérez",
                "phone": "+1234567890",
                "last_visit": "2024-01-10"
            }
        ]
    }

# Ejemplo de integración con base de datos existente
@app.post("/api/appointments")
async def create_appointment(appointment_data: dict):
    """Crear cita (ejemplo de integración con tu base de datos)"""
    try:
        # Aquí conectarías con tu base de datos existente
        appointment = {
            "id": f"apt_{len(appointment_data)}",
            **appointment_data,
            "status": "confirmed"
        }
        
        # Opcional: Notificar a 8n8
        n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL")
        if n8n_webhook_url:
            import requests
            try:
                requests.post(n8n_webhook_url, json=appointment, timeout=5)
            except Exception as e:
                print(f"Error notificando a 8n8: {e}")
        
        return {"success": True, "appointment": appointment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Configuración para Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

"""
INSTRUCCIONES DE INTEGRACIÓN:

1. COPIA EL ARCHIVO:
   - Copia 'fastapi_vapi_integration.py' a tu proyecto
   - Añade 'requests' a tu requirements.txt si no lo tienes

2. AÑADE A TU main.py:
   from fastapi_vapi_integration import add_vapi_routes
   add_vapi_routes(app)

3. CONFIGURA VARIABLES EN RENDER:
   VAPI_API_KEY=tu_api_key
   VAPI_PHONE_NUMBER_ID=tu_phone_id
   VAPI_ASSISTANT_ID=tu_assistant_id
   N8N_WEBHOOK_URL=tu_webhook_8n8 (opcional)

4. ENDPOINTS DISPONIBLES:
   POST /vapi-webhook - Webhook de Vapi
   POST /create-call - Crear llamada
   GET /call-status/{call_id} - Estado de llamada
   GET /appointments - Listar citas
   GET /medical-info - Info del consultorio
   GET /health - Estado del servidor

5. CONFIGURAR EN VAPI:
   - Webhook URL: https://tu-app.onrender.com/vapi-webhook
   - Funciones: get_appointment_info, schedule_appointment, etc.
""" 