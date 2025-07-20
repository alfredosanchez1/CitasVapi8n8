#!/usr/bin/env python3
"""
Karla - Asistente Virtual para Gestión de Citas Médicas
Especializada en hacer, cambiar o cancelar citas para la Dra. Dolores Remedios del Rincón
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import openai
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class KarlaAssistant:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        self.conversation_context = {}
        self.appointment_data = {}
        
        # Inicializar cliente OpenAI
        if self.openai_api_key:
            try:
                self.client = openai.OpenAI(api_key=self.openai_api_key)
                print("✅ Cliente OpenAI inicializado para Karla")
            except Exception as e:
                print(f"❌ Error inicializando cliente OpenAI: {e}")
        
        # Cargar base de conocimiento
        self.knowledge_base = self.load_knowledge_base()
        self.doctor_info = self.load_doctor_info()
        
        # Estado de la conversación
        self.current_step = "greeting"
        self.appointment_flow = {
            "greeting": "Saludo inicial",
            "ask_date_time": "Preguntar día y hora",
            "check_availability": "Verificar disponibilidad",
            "collect_patient_info": "Recopilar información del paciente",
            "confirm_appointment": "Confirmar cita",
            "end": "Finalizar conversación"
        }
    
    def load_knowledge_base(self) -> str:
        """Cargar base de conocimiento desde archivo"""
        try:
            with open("BaseDeConocimiento.txt", "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"❌ Error cargando base de conocimiento: {e}")
            return "Información del consultorio médico."
    
    def load_doctor_info(self) -> str:
        """Cargar información de la doctora"""
        try:
            with open("CurriculumDr.DoloresRemediosdelRincon.txt", "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"❌ Error cargando información de la doctora: {e}")
            return "Dra. Dolores Remedios del Rincón, especialista en Medicina Interna."
    
    def get_system_prompt(self) -> str:
        """Obtener el prompt del sistema para Karla"""
        return f"""
Eres Karla, asistente virtual de la doctora Dolores Remedios del Rincón. Tu función es hacer, cambiar o cancelar citas.

## SALUDO INICIAL
"Hola soy Karla, asistente de la doctora Dolores Remedios del Rincón."

## 1. GESTIÓN DE CITAS
- Consultar disponibilidad de horarios
- Reservar citas nuevas
- Confirmar citas existentes
- Información sobre cancelaciones y reprogramaciones
- Explicar el proceso de primera consulta vs consultas de seguimiento

## PROTOCOLO DE RESERVA DE CITAS

### Información necesaria para agendar:
1. Preguntar primeramente día y hora que quiere hacer la cita.
2. Usar la herramienta Buscar_disponibilidad para obtener fechas y horas disponibles
3. Con las fechas y horas disponibles, preguntar al paciente cual quiere o regresar al punto 1. si no hay fecha u hora disponibles o el paciente no se le acomoden las horas disponibles.   
4. Una vez acordado una fecha y hora con el paciente, preguntar y esperar a que conteste el paciente, uno por uno, cada uno de los siguientes datos:
 
               1. Nombre completo del paciente
               2. Número de teléfono de contacto
               3. Tipo de consulta (primera vez o seguimiento)
               4. Motivo general de la consulta
               5. Disponibilidad de horarios preferidos
               6. Obra social o forma de pago

5. Una vez tomados los datos del paciente se procede a confirmar la cita.

### Confirmación de cita:
- Repetir fecha, hora y tipo de consulta
- Recordar documentos necesarios
- Proporcionar información de contacto para cancelaciones
- Enviar recordatorio si es posible

## RECORDATORIOS IMPORTANTES
- Siempre confirma la información proporcionada
- Sé empático con pacientes ansiosos o preocupados
- Mantén la confidencialidad de la información médica
- Si hay dudas sobre disponibilidad, mejor ofrecer llamar de vuelta con confirmación
- Si el paciente pregunta si eres una persona física, puedes contestar algo como:

   "No, soy un asistente virtual de inteligencia artificial. Mi voz es generada por tecnología de síntesis de voz, pero todas mis respuestas provienen de un sistema de IA. No hay una persona física hablando contigo en este momento."

Principios clave para esta respuesta:
- Transparencia inmediata: Es fundamental ser completamente transparente desde el primer momento. Los usuarios tienen derecho a saber con qué tipo de sistema están interactuando.
- Claridad técnica: Explicar brevemente que la voz es sintética ayuda a disipar cualquier duda sobre la naturaleza de la interacción.
- Evitar ambigüedades: No usar frases como "soy como una persona" o "puedo ayudarte igual que una persona" que puedan generar más confusión.
- Mantener el tono conversacional: Aunque sea una aclaración técnica, mantener un tono amigable y dispuesto a ayudar.

## INFORMACIÓN DE LA DOCTORA
{self.doctor_info}

## BASE DE CONOCIMIENTO
{self.knowledge_base}

## HORARIOS DISPONIBLES
- Lunes a Viernes: 8:00 AM - 6:00 PM
- Sábados: 9:00 AM - 2:00 PM
- Domingos: Cerrado

## DOCUMENTOS NECESARIOS PARA PRIMERA CONSULTA
- Documento de identidad
- Carnet de obra social
- Estudios médicos previos
- Lista de medicamentos actuales
- Resumen de historia clínica (si tiene)

## DOCUMENTOS NECESARIOS PARA CONSULTA DE SEGUIMIENTO
- Documento de identidad
- Carnet de obra social
- Estudios recientes
- Lista actualizada de medicamentos

Responde de manera natural, empática y profesional. Siempre confirma la información antes de proceder.
"""
    
    def check_availability(self, date: str, time: str) -> Dict[str, Any]:
        """Verificar disponibilidad de horarios (simulado)"""
        # Aquí se integraría con Google Calendar
        available_times = [
            "8:00 AM", "9:00 AM", "10:00 AM", "11:00 AM",
            "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM"
        ]
        
        requested_time = time.upper()
        is_available = requested_time in available_times
        
        return {
            "available": is_available,
            "requested_date": date,
            "requested_time": time,
            "available_times": available_times,
            "message": f"El horario {time} está {'disponible' if is_available else 'no disponible'} para el {date}"
        }
    
    def collect_patient_info(self, phone_number: str) -> Dict[str, str]:
        """Recopilar información del paciente"""
        if phone_number in self.appointment_data:
            return self.appointment_data[phone_number]
        return {}
    
    def save_patient_info(self, phone_number: str, info: Dict[str, str]):
        """Guardar información del paciente"""
        self.appointment_data[phone_number] = info
    
    async def generate_response(self, phone_number: str, user_input: str = None, context: Dict = None) -> str:
        """Generar respuesta de Karla"""
        if not self.client:
            return "Lo siento, no puedo procesar tu solicitud en este momento. Un miembro de nuestro equipo se pondrá en contacto contigo pronto."
        
        try:
            # Obtener contexto de conversación
            conversation_context = self.conversation_context.get(phone_number, {
                "step": "greeting",
                "appointment_data": {},
                "messages": []
            })
            
            # Agregar mensaje del usuario
            if user_input:
                conversation_context["messages"].append({"role": "user", "content": user_input})
            
            # Construir mensajes para OpenAI
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "assistant", "content": "Hola soy Karla, asistente de la doctora Dolores Remedios del Rincón. ¿En qué puedo ayudarte hoy?"}
            ]
            
            # Agregar historial de conversación
            for msg in conversation_context["messages"][-5:]:  # Últimos 5 mensajes
                messages.append(msg)
            
            # Generar respuesta
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            karla_response = response.choices[0].message.content
            
            # Actualizar contexto
            conversation_context["messages"].append({"role": "assistant", "content": karla_response})
            self.conversation_context[phone_number] = conversation_context
            
            return karla_response
            
        except Exception as e:
            print(f"❌ Error generando respuesta de Karla: {e}")
            return "Lo siento, estoy teniendo dificultades técnicas. Un miembro de nuestro equipo se pondrá en contacto contigo pronto."
    
    async def handle_appointment_request(self, phone_number: str, user_input: str) -> str:
        """Manejar solicitud de cita específicamente"""
        try:
            # Verificar si es primera vez o seguimiento
            if "primera vez" in user_input.lower() or "primera consulta" in user_input.lower():
                return await self.handle_first_time_appointment(phone_number, user_input)
            elif "seguimiento" in user_input.lower() or "control" in user_input.lower():
                return await self.handle_follow_up_appointment(phone_number, user_input)
            else:
                return await self.generate_response(phone_number, user_input)
                
        except Exception as e:
            print(f"❌ Error manejando solicitud de cita: {e}")
            return "Lo siento, estoy teniendo dificultades. Un miembro de nuestro equipo se pondrá en contacto contigo pronto."
    
    async def handle_first_time_appointment(self, phone_number: str, user_input: str) -> str:
        """Manejar cita de primera vez"""
        return await self.generate_response(phone_number, 
            f"Entiendo que necesitas una cita de primera vez. {user_input}. Te ayudo a agendar tu cita. ¿Qué día te gustaría venir?")
    
    async def handle_follow_up_appointment(self, phone_number: str, user_input: str) -> str:
        """Manejar cita de seguimiento"""
        return await self.generate_response(phone_number, 
            f"Perfecto, cita de seguimiento. {user_input}. ¿Qué día te gustaría venir para tu control?")
    
    def get_appointment_confirmation(self, appointment_data: Dict[str, str]) -> str:
        """Generar confirmación de cita"""
        return f"""
Perfecto, tu cita ha sido confirmada:

📅 Fecha: {appointment_data.get('date', 'Por confirmar')}
🕐 Hora: {appointment_data.get('time', 'Por confirmar')}
👤 Paciente: {appointment_data.get('name', 'Por confirmar')}
📞 Teléfono: {appointment_data.get('phone', 'Por confirmar')}
🏥 Tipo: {appointment_data.get('type', 'Por confirmar')}
💳 Pago: {appointment_data.get('payment', 'Por confirmar')}

📋 Documentos necesarios:
- Documento de identidad
- Carnet de obra social
- Estudios médicos previos
- Lista de medicamentos actuales

📞 Para cancelaciones: Llama al mismo número
⏰ Recuerda llegar 10 minutos antes

¿Algo más en lo que pueda ayudarte?
"""

# Instancia global de Karla
karla_assistant = KarlaAssistant() 