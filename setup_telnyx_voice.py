#!/usr/bin/env python3
"""
Script para configurar Telnyx Voice API y crear llamadas programáticamente
"""

import os
import asyncio
import aiohttp
from dotenv import load_dotenv
import json

# Cargar variables de entorno
load_dotenv()

# Configuración de Telnyx
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
WEBHOOK_URL = "https://web-production-a2b02.up.railway.app/telnyx-webhook"

class TelnyxVoiceManager:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.telnyx.com/v2"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_call(self, from_number: str, to_number: str, webhook_url: str = None):
        """Crear una llamada saliente"""
        if not webhook_url:
            webhook_url = WEBHOOK_URL
        
        url = f"{self.base_url}/calls"
        
        payload = {
            "from": from_number,
            "to": to_number,
            "webhook_url": webhook_url,
            "webhook_url_timeout": 30,
            "webhook_url_method": "POST"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=self.headers) as response:
                    print(f"📞 Creando llamada: {response.status}")
                    if response.status == 201:
                        result = await response.json()
                        print(f"✅ Llamada creada: {json.dumps(result, indent=2)}")
                        return result
                    else:
                        error_text = await response.text()
                        print(f"❌ Error creando llamada: {error_text}")
                        return None
        except Exception as e:
            print(f"❌ Error en create_call: {e}")
            return None
    
    async def get_call_status(self, call_control_id: str):
        """Obtener estado de una llamada"""
        url = f"{self.base_url}/calls/{call_control_id}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    print(f"📊 Estado de llamada: {response.status}")
                    if response.status == 200:
                        result = await response.json()
                        print(f"📊 Estado: {json.dumps(result, indent=2)}")
                        return result
                    else:
                        error_text = await response.text()
                        print(f"❌ Error obteniendo estado: {error_text}")
                        return None
        except Exception as e:
            print(f"❌ Error en get_call_status: {e}")
            return None
    
    async def hangup_call(self, call_control_id: str):
        """Colgar una llamada"""
        url = f"{self.base_url}/calls/{call_control_id}/actions"
        
        payload = {
            "hangup": {}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=self.headers) as response:
                    print(f"📞 Colgando llamada: {response.status}")
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Llamada colgada: {json.dumps(result, indent=2)}")
                        return result
                    else:
                        error_text = await response.text()
                        print(f"❌ Error colgando llamada: {error_text}")
                        return None
        except Exception as e:
            print(f"❌ Error en hangup_call: {e}")
            return None
    
    async def speak_text(self, call_control_id: str, text: str):
        """Hacer que el sistema hable"""
        url = f"{self.base_url}/calls/{call_control_id}/actions"
        
        payload = {
            "speak": {
                "payload": text,
                "voice": "alice",
                "language": "es-MX"
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=self.headers) as response:
                    print(f"🗣️ Hablando: {response.status}")
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Hablado: {json.dumps(result, indent=2)}")
                        return result
                    else:
                        error_text = await response.text()
                        print(f"❌ Error hablando: {error_text}")
                        return None
        except Exception as e:
            print(f"❌ Error en speak_text: {e}")
            return None
    
    async def start_speech_recognition(self, call_control_id: str):
        """Iniciar reconocimiento de voz"""
        url = f"{self.base_url}/calls/{call_control_id}/actions"
        
        payload = {
            "gather_using_speak": {
                "speech": {
                    "language": "es-MX",
                    "interim_results": False,
                    "end_of_speech_detection": True
                },
                "speak": {
                    "payload": "Estoy escuchando...",
                    "voice": "alice",
                    "language": "es-MX"
                }
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=self.headers) as response:
                    print(f"👂 Escuchando: {response.status}")
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Escuchando: {json.dumps(result, indent=2)}")
                        return result
                    else:
                        error_text = await response.text()
                        print(f"❌ Error escuchando: {error_text}")
                        return None
        except Exception as e:
            print(f"❌ Error en start_speech_recognition: {e}")
            return None

async def test_voice_api():
    """Función de prueba para la API de voz"""
    if not TELNYX_API_KEY:
        print("❌ TELNYX_API_KEY no configurada")
        return
    
    manager = TelnyxVoiceManager(TELNYX_API_KEY)
    
    # Números de prueba (reemplazar con números reales)
    from_number = "+526624920537"  # Tu número de Telnyx
    to_number = "+526622563607"    # Número de destino
    
    print(f"🧪 Probando Voice API...")
    print(f"   Desde: {from_number}")
    print(f"   Hacia: {to_number}")
    print(f"   Webhook: {WEBHOOK_URL}")
    
    # Crear llamada
    call_result = await manager.create_call(from_number, to_number)
    
    if call_result:
        call_control_id = call_result.get('data', {}).get('call_control_id')
        print(f"📞 Call Control ID: {call_control_id}")
        
        # Esperar un poco para que la llamada se establezca
        await asyncio.sleep(5)
        
        # Obtener estado
        await manager.get_call_status(call_control_id)
        
        # Esperar más tiempo para que termine la llamada
        await asyncio.sleep(30)
        
        # Obtener estado final
        await manager.get_call_status(call_control_id)

async def test_simple_call():
    """Prueba simple de llamada"""
    if not TELNYX_API_KEY:
        print("❌ TELNYX_API_KEY no configurada")
        return
    
    manager = TelnyxVoiceManager(TELNYX_API_KEY)
    
    # Crear llamada simple
    from_number = "+526624920537"
    to_number = "+526622563607"
    
    print(f"📞 Creando llamada simple...")
    call_result = await manager.create_call(from_number, to_number)
    
    if call_result:
        print("✅ Llamada creada exitosamente")
        print(f"📊 Resultado: {json.dumps(call_result, indent=2)}")
    else:
        print("❌ Error creando llamada")

if __name__ == "__main__":
    print("🚀 Telnyx Voice API Setup")
    print("=" * 50)
    
    # Verificar configuración
    if not TELNYX_API_KEY:
        print("❌ TELNYX_API_KEY no encontrada en variables de entorno")
        print("💡 Agrega TELNYX_API_KEY=tu_api_key a tu archivo .env")
    else:
        print("✅ TELNYX_API_KEY configurada")
        print(f"🔗 Webhook URL: {WEBHOOK_URL}")
        
        # Ejecutar prueba
        asyncio.run(test_simple_call()) 