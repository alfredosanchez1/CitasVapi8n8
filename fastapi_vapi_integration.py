"""
Integración Vapi + FastAPI para Consultorio Médico
Añade este código a tu aplicación FastAPI existente
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import requests
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de Vapi
VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_PHONE_NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
VAPI_ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")
VAPI_BASE_URL = "https://api.vapi.ai"

# Modelos Pydantic
class CallRequest(BaseModel):
    phone_number: str
    patient_name: Optional[str] = None
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class VapiWebhook(BaseModel):
    type: str
    callId: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class AppointmentRequest(BaseModel):
    patient_name: str
    phone: str
    date: str
    time: str
    reason: Optional[str] = "Consulta general"

# Base de conocimiento del consultorio
MEDICAL_KNOWLEDGE = {
    "horarios": {
        "lunes_viernes": "8:00 a 18:00",
        "sabados": "9:00 a 14:00",
        "domingos": "Cerrado"
    },
    "ubicacion": "Estamos ubicados en [DIRECCIÓN COMPLETA]. Contamos con estacionamiento disponible.",
    "doctor": "Dr. Xavier Xijemez Xifra - Médico Especialista en Medicina Interna",
    "especialidades": [
        "Diabetes Mellitus tipo 1 y 2",
        "Hipertensión arterial", 
        "Enfermedades cardiovasculares",
        "Problemas respiratorios",
        "Trastornos endocrinos",
        "Medicina preventiva"
    ],
    "preparacion_consulta": [
        "Documento de identidad",
        "Carnet de obra social", 
        "Estudios médicos previos",
        "Lista de medicamentos actuales",
        "Resumen de historia clínica"
    ]
}

# Funciones de Vapi
def create_vapi_call(phone_number: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
    """Crear una llamada usando Vapi"""
    try:
        if not VAPI_API_KEY:
            raise HTTPException(status_code=500, detail="VAPI_API_KEY no configurada")
        
        headers = {
            "Authorization": f"Bearer {VAPI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "phoneNumberId": VAPI_PHONE_NUMBER_ID,
            "assistantId": VAPI_ASSISTANT_ID,
            "customer": {
                "number": phone_number
            }
        }
        
        if metadata:
            payload["metadata"] = metadata
        
        response = requests.post(
            f"{VAPI_BASE_URL}/call",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error Vapi: {response.status_code} - {response.text}")
            raise HTTPException(status_code=500, detail="Error creando llamada en Vapi")
            
    except Exception as e:
        logger.error(f"Excepción creando llamada: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def get_vapi_call_status(call_id: str) -> Dict[str, Any]:
    """Obtener estado de una llamada de Vapi"""
    try:
        headers = {
            "Authorization": f"Bearer {VAPI_API_KEY}"
        }
        
        response = requests.get(
            f"{VAPI_BASE_URL}/call/{call_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status code: {response.status_code}"}
            
    except Exception as e:
        return {"error": str(e)}

# Funciones del consultorio médico
def handle_medical_function(function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Manejar funciones específicas del consultorio médico"""
    
    if function_name == "get_appointment_info":
        return {
            "horarios": MEDICAL_KNOWLEDGE["horarios"],
            "ubicacion": MEDICAL_KNOWLEDGE["ubicacion"],
            "doctor": MEDICAL_KNOWLEDGE["doctor"],
            "preparacion": MEDICAL_KNOWLEDGE["preparacion_consulta"]
        }
    
    elif function_name == "schedule_appointment":
        return schedule_appointment(arguments)
    
    elif function_name == "get_doctor_info":
        return {
            "name": "Dr. Xavier Xijemez Xifra",
            "specialty": "Medicina Interna",
            "experience": "Más de 5,000 consultas realizadas",
            "certifications": [
                "Consejo Mexicano de Medicina Interna",
                "Colegio de Medicina Interna de México A.C.",
                "Asociación Mexicana de Diabetes"
            ],
            "education": [
                "UNAM - Facultad de Medicina",
                "Hospital General de México - Residencia", 
                "Diplomado en Diabetes y Endocrinología"
            ]
        }
    
    elif function_name == "get_specialties":
        return {
            "specialties": MEDICAL_KNOWLEDGE["especialidades"],
            "description": "Especialista en medicina interna con enfoque en atención integral del paciente adulto"
        }
    
    elif function_name == "check_availability":
        return check_availability(arguments)
    
    else:
        return {"error": f"Función no encontrada: {function_name}"}

def schedule_appointment(args: Dict[str, Any]) -> Dict[str, Any]:
    """Programar una cita médica"""
    try:
        patient_name = args.get("patient_name", "Sin nombre")
        phone = args.get("phone", "")
        date = args.get("date", "")
        time = args.get("time", "")
        reason = args.get("reason", "Consulta general")
        
        # Aquí integrarías con tu base de datos o 8n8
        appointment = {
            "id": f"apt_{hash(phone + date + time)}",
            "patient_name": patient_name,
            "phone": phone,
            "date": date,
            "time": time,
            "reason": reason,
            "status": "confirmed",
            "created_at": datetime.now().isoformat()
        }
        
        # Simular guardado (aquí conectarías con tu base de datos)
        logger.info(f"Cita programada: {appointment}")
        
        # Opcional: Notificar a 8n8
        notify_8n8(appointment)
        
        return {
            "success": True,
            "appointment": appointment,
            "message": f"Cita confirmada para {patient_name} el {date} a las {time}"
        }
        
    except Exception as e:
        logger.error(f"Error programando cita: {str(e)}")
        return {"error": "Error programando cita"}

def check_availability(args: Dict[str, Any]) -> Dict[str, Any]:
    """Verificar disponibilidad de horarios"""
    date = args.get("date", "")
    time = args.get("time", "")
    
    # Simular verificación de disponibilidad
    # Aquí conectarías con tu sistema de calendario
    
    available_slots = [
        "09:00", "10:00", "11:00", "12:00",
        "14:00", "15:00", "16:00", "17:00"
    ]
    
    return {
        "date": date,
        "available_slots": available_slots,
        "is_available": time in available_slots if time else True
    }

def notify_8n8(appointment_data: Dict[str, Any]):
    """Notificar a 8n8 sobre nueva cita (opcional)"""
    n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL")
    if n8n_webhook_url:
        try:
            requests.post(n8n_webhook_url, json=appointment_data, timeout=5)
            logger.info("Notificación enviada a 8n8")
        except Exception as e:
            logger.error(f"Error notificando a 8n8: {str(e)}")

def process_vapi_webhook(webhook_data: Dict[str, Any]) -> Dict[str, Any]:
    """Procesar webhook de Vapi"""
    try:
        event_type = webhook_data.get("type")
        
        if event_type == "function-call":
            function_name = webhook_data.get("data", {}).get("name")
            arguments = webhook_data.get("data", {}).get("arguments", {})
            
            result = handle_medical_function(function_name, arguments)
            return {"result": result}
        
        elif event_type == "call-started":
            call_id = webhook_data.get("callId")
            logger.info(f"Llamada iniciada: {call_id}")
            return {"status": "processed", "message": "Call started"}
            
        elif event_type == "call-ended":
            call_id = webhook_data.get("callId")
            logger.info(f"Llamada terminada: {call_id}")
            return {"status": "processed", "message": "Call ended"}
            
        elif event_type == "speech-start":
            logger.info("Usuario empezó a hablar")
            return {"status": "processed", "message": "Speech started"}
            
        elif event_type == "speech-end":
            logger.info("Usuario terminó de hablar")
            return {"status": "processed", "message": "Speech ended"}
            
        else:
            logger.info(f"Evento ignorado: {event_type}")
            return {"status": "ignored", "message": f"Unknown event type: {event_type}"}
            
    except Exception as e:
        logger.error(f"Error procesando webhook: {str(e)}")
        return {"error": str(e)}

# Endpoints para añadir a tu FastAPI app
def add_vapi_routes(app: FastAPI):
    """Añadir rutas de Vapi a tu aplicación FastAPI"""
    
    @app.post("/vapi-webhook")
    async def vapi_webhook(request: Request):
        """Endpoint para recibir webhooks de Vapi"""
        try:
            webhook_data = await request.json()
            result = process_vapi_webhook(webhook_data)
            return result
        except Exception as e:
            logger.error(f"Error en webhook: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.post("/create-call")
    async def create_call(call_request: CallRequest):
        """Crear una llamada médica"""
        try:
            metadata = {
                "type": "medical_consultation",
                "patient_name": call_request.patient_name,
                "reason": call_request.reason
            }
            
            if call_request.metadata:
                metadata.update(call_request.metadata)
            
            result = create_vapi_call(call_request.phone_number, metadata)
            return {
                "success": True,
                "message": "Llamada iniciada",
                "call_data": result
            }
        except Exception as e:
            logger.error(f"Error creando llamada: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/call-status/{call_id}")
    async def get_call_status(call_id: str):
        """Obtener estado de una llamada"""
        try:
            result = get_vapi_call_status(call_id)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
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
    
    @app.get("/medical-info")
    async def get_medical_info():
        """Obtener información del consultorio"""
        return {
            "consultorio": "Dr. Xavier Xijemez Xifra",
            "especialidad": "Medicina Interna",
            "horarios": MEDICAL_KNOWLEDGE["horarios"],
            "ubicacion": MEDICAL_KNOWLEDGE["ubicacion"],
            "especialidades": MEDICAL_KNOWLEDGE["especialidades"]
        }
    
    @app.get("/health")
    async def health_check():
        """Verificar estado del servidor"""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "vapi_configured": bool(VAPI_API_KEY)
        }

# Ejemplo de uso en tu app principal
"""
# En tu main.py o app.py
from fastapi import FastAPI
from fastapi_vapi_integration import add_vapi_routes

app = FastAPI(title="Consultorio Médico API")

# Añadir rutas de Vapi
add_vapi_routes(app)

# Tus otras rutas aquí...

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
""" 