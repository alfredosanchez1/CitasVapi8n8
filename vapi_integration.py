"""
Módulo de integración con Vapi para consultorio médico
Añade este archivo a tu API existente en Render
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VapiIntegration:
    def __init__(self):
        self.api_key = os.getenv("VAPI_API_KEY")
        self.phone_number_id = os.getenv("VAPI_PHONE_NUMBER_ID")
        self.assistant_id = os.getenv("VAPI_ASSISTANT_ID")
        self.base_url = "https://api.vapi.ai"
        
        if not self.api_key:
            logger.warning("VAPI_API_KEY no configurada")
    
    def create_call(self, phone_number: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Crear una llamada usando Vapi"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "phoneNumberId": self.phone_number_id,
                "assistantId": self.assistant_id,
                "customer": {
                    "number": phone_number
                }
            }
            
            if metadata:
                payload["metadata"] = metadata
            
            response = requests.post(
                f"{self.base_url}/call",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error creando llamada: {response.status_code} - {response.text}")
                return {"error": "Failed to create call"}
                
        except Exception as e:
            logger.error(f"Excepción creando llamada: {str(e)}")
            return {"error": str(e)}
    
    def get_call_status(self, call_id: str) -> Dict[str, Any]:
        """Obtener estado de una llamada"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.get(
                f"{self.base_url}/call/{call_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Status code: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}

class MedicalConsultationHandler:
    """Manejador de consultas médicas para Vapi"""
    
    def __init__(self):
        # Base de conocimiento del consultorio
        self.knowledge_base = {
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
    
    def handle_function_call(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Manejar llamadas a funciones desde Vapi"""
        
        if function_name == "get_appointment_info":
            return self.get_appointment_info()
            
        elif function_name == "schedule_appointment":
            return self.schedule_appointment(arguments)
            
        elif function_name == "get_doctor_info":
            return self.get_doctor_info()
            
        elif function_name == "get_specialties":
            return self.get_specialties()
            
        elif function_name == "check_availability":
            return self.check_availability(arguments)
            
        else:
            return {"error": f"Función no encontrada: {function_name}"}
    
    def get_appointment_info(self) -> Dict[str, Any]:
        """Obtener información general de citas"""
        return {
            "horarios": self.knowledge_base["horarios"],
            "ubicacion": self.knowledge_base["ubicacion"],
            "doctor": self.knowledge_base["doctor"],
            "preparacion": self.knowledge_base["preparacion_consulta"]
        }
    
    def schedule_appointment(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Programar una cita"""
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
            
            return {
                "success": True,
                "appointment": appointment,
                "message": f"Cita confirmada para {patient_name} el {date} a las {time}"
            }
            
        except Exception as e:
            logger.error(f"Error programando cita: {str(e)}")
            return {"error": "Error programando cita"}
    
    def get_doctor_info(self) -> Dict[str, Any]:
        """Obtener información del doctor"""
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
    
    def get_specialties(self) -> Dict[str, Any]:
        """Obtener especialidades del consultorio"""
        return {
            "specialties": self.knowledge_base["especialidades"],
            "description": "Especialista en medicina interna con enfoque en atención integral del paciente adulto"
        }
    
    def check_availability(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Verificar disponibilidad de horarios"""
        date = args.get("date", "")
        time = args.get("time", "")
        
        # Simular verificación de disponibilidad
        # Aquí conectarías con tu sistema de calendario
        
        # Por ahora, simulamos que hay disponibilidad
        available_slots = [
            "09:00", "10:00", "11:00", "12:00",
            "14:00", "15:00", "16:00", "17:00"
        ]
        
        return {
            "date": date,
            "available_slots": available_slots,
            "is_available": time in available_slots if time else True
        }

# Instancias globales
vapi_client = VapiIntegration()
consultation_handler = MedicalConsultationHandler()

def process_vapi_webhook(webhook_data: Dict[str, Any]) -> Dict[str, Any]:
    """Procesar webhook de Vapi"""
    try:
        event_type = webhook_data.get("type")
        
        if event_type == "function-call":
            function_name = webhook_data.get("data", {}).get("name")
            arguments = webhook_data.get("data", {}).get("arguments", {})
            
            result = consultation_handler.handle_function_call(function_name, arguments)
            return {"result": result}
        
        elif event_type == "call-started":
            logger.info(f"Llamada iniciada: {webhook_data.get('callId')}")
            return {"status": "processed"}
            
        elif event_type == "call-ended":
            logger.info(f"Llamada terminada: {webhook_data.get('callId')}")
            return {"status": "processed"}
            
        else:
            logger.info(f"Evento ignorado: {event_type}")
            return {"status": "ignored"}
            
    except Exception as e:
        logger.error(f"Error procesando webhook: {str(e)}")
        return {"error": str(e)}

def create_medical_call(phone_number: str, patient_info: Optional[Dict] = None) -> Dict[str, Any]:
    """Crear una llamada médica"""
    metadata = {
        "type": "medical_consultation",
        "patient_info": patient_info or {}
    }
    
    return vapi_client.create_call(phone_number, metadata) 