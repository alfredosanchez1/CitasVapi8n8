"""
Sistema de gestión de citas con Google Calendar
"""

import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Scopes para Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarManager:
    def __init__(self):
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        self.credentials = None
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Autenticar con Google Calendar"""
        try:
            # Cargar credenciales desde archivo
            creds = None
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
            # Si no hay credenciales válidas, hacer el flujo de autenticación
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Guardar credenciales para la próxima ejecución
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            
            self.credentials = creds
            self.service = build('calendar', 'v3', credentials=creds)
            logger.info("✅ Autenticación con Google Calendar exitosa")
            
        except Exception as e:
            logger.error(f"❌ Error autenticando con Google Calendar: {e}")
            self.service = None
    
    def get_available_slots(self, date: str, duration_minutes: int = 30) -> List[Dict[str, Any]]:
        """Obtener horarios disponibles para una fecha específica"""
        try:
            if not self.service:
                logger.error("Servicio de Google Calendar no disponible")
                return []
            
            # Convertir fecha a datetime
            start_date = datetime.strptime(date, "%Y-%m-%d")
            end_date = start_date + timedelta(days=1)
            
            # Horarios de trabajo
            work_start = start_date.replace(hour=8, minute=0)  # 8:00 AM
            work_end = start_date.replace(hour=18, minute=0)   # 6:00 PM
            
            # Obtener eventos existentes para esa fecha
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=work_start.isoformat() + 'Z',
                timeMax=work_end.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Generar slots disponibles
            available_slots = []
            current_time = work_start
            
            while current_time < work_end:
                slot_end = current_time + timedelta(minutes=duration_minutes)
                
                # Verificar si el slot está disponible
                is_available = True
                for event in events:
                    event_start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
                    event_end = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')))
                    
                    # Verificar si hay conflicto
                    if (current_time < event_end and slot_end > event_start):
                        is_available = False
                        break
                
                if is_available:
                    available_slots.append({
                        'start_time': current_time.strftime('%H:%M'),
                        'end_time': slot_end.strftime('%H:%M'),
                        'datetime': current_time.isoformat()
                    })
                
                current_time = slot_end
            
            return available_slots
            
        except Exception as e:
            logger.error(f"Error obteniendo slots disponibles: {e}")
            return []
    
    def create_appointment(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear una cita en Google Calendar"""
        try:
            if not self.service:
                logger.error("Servicio de Google Calendar no disponible")
                return {"success": False, "error": "Servicio no disponible"}
            
            # Extraer datos de la cita
            patient_name = appointment_data.get('nombre', 'Paciente')
            phone = appointment_data.get('telefono', '')
            reason = appointment_data.get('motivo', 'Consulta médica')
            date = appointment_data.get('fecha', datetime.now().strftime('%Y-%m-%d'))
            time = appointment_data.get('hora', '10:00')
            
            # Crear datetime para la cita
            appointment_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            end_datetime = appointment_datetime + timedelta(minutes=30)
            
            # Crear evento en Google Calendar
            event = {
                'summary': f'Cita: {patient_name}',
                'description': f'Motivo: {reason}\nTeléfono: {phone}',
                'start': {
                    'dateTime': appointment_datetime.isoformat(),
                    'timeZone': 'America/Mexico_City',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'America/Mexico_City',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 día antes
                        {'method': 'popup', 'minutes': 30},       # 30 min antes
                    ],
                },
            }
            
            event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            logger.info(f"✅ Cita creada: {event.get('htmlLink')}")
            
            return {
                "success": True,
                "event_id": event.get('id'),
                "event_link": event.get('htmlLink'),
                "start_time": appointment_datetime.strftime('%Y-%m-%d %H:%M'),
                "end_time": end_datetime.strftime('%Y-%m-%d %H:%M')
            }
            
        except Exception as e:
            logger.error(f"Error creando cita: {e}")
            return {"success": False, "error": str(e)}
    
    def get_appointments_for_date(self, date: str) -> List[Dict[str, Any]]:
        """Obtener todas las citas para una fecha específica"""
        try:
            if not self.service:
                return []
            
            start_date = datetime.strptime(date, "%Y-%m-%d")
            end_date = start_date + timedelta(days=1)
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            appointments = []
            for event in events:
                if 'Cita:' in event.get('summary', ''):
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    end = event['end'].get('dateTime', event['end'].get('date'))
                    
                    appointments.append({
                        'id': event['id'],
                        'patient_name': event['summary'].replace('Cita: ', ''),
                        'start_time': start,
                        'end_time': end,
                        'description': event.get('description', ''),
                        'link': event.get('htmlLink', '')
                    })
            
            return appointments
            
        except Exception as e:
            logger.error(f"Error obteniendo citas: {e}")
            return []
    
    def cancel_appointment(self, event_id: str) -> Dict[str, Any]:
        """Cancelar una cita"""
        try:
            if not self.service:
                return {"success": False, "error": "Servicio no disponible"}
            
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            logger.info(f"✅ Cita cancelada: {event_id}")
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Error cancelando cita: {e}")
            return {"success": False, "error": str(e)}
    
    def get_next_available_date(self, start_date: str = None) -> str:
        """Obtener la próxima fecha disponible"""
        try:
            if not start_date:
                start_date = datetime.now().strftime('%Y-%m-%d')
            
            current_date = datetime.strptime(start_date, '%Y-%m-%d')
            
            # Buscar en los próximos 30 días
            for i in range(30):
                check_date = current_date + timedelta(days=i)
                check_date_str = check_date.strftime('%Y-%m-%d')
                
                # Verificar si es día laboral (lunes a sábado)
                if check_date.weekday() < 6:  # 0-5 = lunes a sábado
                    available_slots = self.get_available_slots(check_date_str)
                    if available_slots:
                        return check_date_str
            
            return start_date  # Si no encuentra nada, devolver la fecha original
            
        except Exception as e:
            logger.error(f"Error obteniendo próxima fecha disponible: {e}")
            return start_date or datetime.now().strftime('%Y-%m-%d')

# Instancia global del manager
calendar_manager = GoogleCalendarManager() 