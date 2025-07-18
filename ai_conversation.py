"""
Sistema de conversación con IA usando OpenAI
"""

import os
import json
from typing import Dict, Any, Optional
from openai import OpenAI
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIConversationManager:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.conversation_contexts = {}
        
        # Prompt base para el asistente médico
        self.base_prompt = """Eres una asistente virtual del Consultorio Médico del Dr. Xavier Xijemez Xifra.
        
        Tu objetivo es ayudar a los pacientes a agendar citas y responder sus consultas de manera profesional y cálida.
        
        INFORMACIÓN DEL CONSULTORIO:
        - Horarios: Lunes a viernes de 8:00 a 18:00, Sábados de 9:00 a 14:00
        - Ubicación: [DIRECCIÓN DEL CONSULTORIO]
        - Para primera consulta: traer documento de identidad, carnet de obra social, estudios previos
        - Emergencias: acudir al servicio de urgencias más cercano
        
        INSTRUCCIONES:
        1. Saluda amablemente al paciente
        2. Si quiere agendar cita: recopila nombre, teléfono, motivo de consulta
        3. Si pregunta por horarios, ubicación, etc.: proporciona la información
        4. Sé profesional pero cálida
        5. Habla en español mexicano
        6. Confirma la información antes de terminar
        
        CONTEXTO DE LA CONVERSACIÓN:
        - Esta es la llamada número {step} del paciente
        - Número de teléfono: {phone_number}
        - Información previa: {previous_info}
        
        Responde de manera natural y conversacional, como si fuera una conversación real por teléfono."""
    
    def get_conversation_context(self, phone_number: str) -> Dict[str, Any]:
        """Obtener contexto de conversación para un número de teléfono"""
        if phone_number not in self.conversation_contexts:
            self.conversation_contexts[phone_number] = {
                "step": 0,
                "data": {},
                "conversation_history": []
            }
        return self.conversation_contexts[phone_number]
    
    def update_conversation_context(self, phone_number: str, step: int, data: Dict[str, Any] = None):
        """Actualizar contexto de conversación"""
        if phone_number not in self.conversation_contexts:
            self.conversation_contexts[phone_number] = {
                "step": 0,
                "data": {},
                "conversation_history": []
            }
        
        self.conversation_contexts[phone_number]["step"] = step
        if data:
            self.conversation_contexts[phone_number]["data"].update(data)
    
    def add_to_conversation_history(self, phone_number: str, message: str, is_user: bool = False):
        """Agregar mensaje al historial de conversación"""
        context = self.get_conversation_context(phone_number)
        context["conversation_history"].append({
            "message": message,
            "is_user": is_user,
            "timestamp": datetime.now().isoformat()
        })
    
    async def generate_response(self, phone_number: str, user_input: str = None) -> str:
        """Generar respuesta usando OpenAI"""
        try:
            context = self.get_conversation_context(phone_number)
            step = context["step"]
            
            # Si es la primera llamada y no hay input del usuario, generar saludo
            if step == 0 and not user_input:
                return await self._generate_greeting(phone_number)
            
            # Construir el prompt con contexto
            prompt = self._build_prompt(phone_number, user_input)
            
            # Llamar a OpenAI
            response = await self._call_openai(prompt)
            
            # Actualizar contexto
            if user_input:
                self.add_to_conversation_history(phone_number, user_input, is_user=True)
            self.add_to_conversation_history(phone_number, response, is_user=False)
            
            # Incrementar paso
            self.update_conversation_context(phone_number, step + 1)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generando respuesta con OpenAI: {e}")
            return self._get_fallback_response(step)
    
    async def _generate_greeting(self, phone_number: str) -> str:
        """Generar saludo inicial"""
        prompt = self.base_prompt.format(
            step=0,
            phone_number=phone_number,
            previous_info="Primera llamada"
        )
        
        try:
            response = await self._call_openai(prompt + "\n\nGenera un saludo inicial amable y profesional.")
            self.update_conversation_context(phone_number, 1)
            return response
        except Exception as e:
            logger.error(f"Error generando saludo: {e}")
            return self._get_fallback_response(0)
    
    def _build_prompt(self, phone_number: str, user_input: str = None) -> str:
        """Construir prompt para OpenAI"""
        context = self.get_conversation_context(phone_number)
        step = context["step"]
        history = context["conversation_history"]
        
        # Construir historial de conversación
        conversation_text = ""
        for msg in history[-5:]:  # Últimos 5 mensajes
            role = "Usuario" if msg["is_user"] else "Asistente"
            conversation_text += f"{role}: {msg['message']}\n"
        
        if user_input:
            conversation_text += f"Usuario: {user_input}\n"
        
        prompt = self.base_prompt.format(
            step=step,
            phone_number=phone_number,
            previous_info=str(context["data"])
        )
        
        prompt += f"\n\nHISTORIAL DE CONVERSACIÓN:\n{conversation_text}\n\nAsistente:"
        
        return prompt
    
    async def _call_openai(self, prompt: str) -> str:
        """Llamar a OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres una asistente virtual médica profesional y cálida."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error llamando a OpenAI: {e}")
            raise e
    
    def _get_fallback_response(self, step: int) -> str:
        """Respuesta de respaldo si OpenAI falla"""
        fallback_responses = {
            0: "¡Hola! Bienvenido al Consultorio del Dr. Xavier Xijemez Xifra. ¿En qué puedo ayudarle?",
            1: "Perfecto, entiendo que desea agendar una cita. Un miembro de nuestro equipo se pondrá en contacto con usted.",
            2: "Excelente, he tomado nota de su información. Recibirá una confirmación pronto.",
            3: "Gracias por su confianza. Que tenga un excelente día."
        }
        
        return fallback_responses.get(step, "Gracias por llamar. Que tenga un excelente día.")
    
    def extract_appointment_info(self, conversation_text: str) -> Dict[str, Any]:
        """Extraer información de cita del texto de conversación"""
        try:
            # Usar OpenAI para extraer información estructurada
            prompt = f"""
            Extrae la siguiente información de la conversación:
            - Nombre del paciente
            - Número de teléfono
            - Motivo de consulta
            - Fecha preferida (si se menciona)
            - Hora preferida (si se menciona)
            
            Conversación: {conversation_text}
            
            Responde en formato JSON:
            {{
                "nombre": "string",
                "telefono": "string", 
                "motivo": "string",
                "fecha_preferida": "string o null",
                "hora_preferida": "string o null"
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extrae información estructurada de conversaciones médicas."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return result
            
        except Exception as e:
            logger.error(f"Error extrayendo información de cita: {e}")
            return {
                "nombre": None,
                "telefono": None,
                "motivo": None,
                "fecha_preferida": None,
                "hora_preferida": None
            }

# Instancia global del manager
ai_manager = AIConversationManager() 