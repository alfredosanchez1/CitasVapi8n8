#!/usr/bin/env python3
"""
Script para configurar Telnyx con la API key proporcionada
"""

import os
import asyncio
import aiohttp
import json

# API Key de Telnyx proporcionada
TELNYX_API_KEY = "KEY019824F7A25307988B858E8EFE273309_bhA8IL88RjFzlsLFWcC6gS"

class TelnyxSetup:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.telnyx.com/v2"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def get_phone_numbers(self):
        """Obtener números de teléfono configurados"""
        url = f"{self.base_url}/phone_numbers"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('data', [])
                    else:
                        print(f"❌ Error obteniendo números: {response.status}")
                        return []
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    async def configure_webhook(self, phone_number_id: str, webhook_url: str):
        """Configurar webhook para un número de teléfono"""
        url = f"{self.base_url}/phone_numbers/{phone_number_id}"
        
        payload = {
            "webhook_url": webhook_url,
            "webhook_url_timeout": 30,
            "webhook_url_method": "POST"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.patch(url, json=payload, headers=self.headers) as response:
                    if response.status == 200:
                        print(f"✅ Webhook configurado para {phone_number_id}")
                        return True
                    else:
                        error_text = await response.text()
                        print(f"❌ Error configurando webhook: {error_text}")
                        return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    async def test_webhook(self, webhook_url: str):
        """Probar que el webhook funciona"""
        test_data = {
            "event_type": "test",
            "data": {
                "test": "data"
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=test_data) as response:
                    if response.status == 200:
                        print(f"✅ Webhook funciona correctamente")
                        return True
                    else:
                        print(f"❌ Webhook no responde: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Error probando webhook: {e}")
            return False

async def main():
    print("🚀 Configuración de Telnyx")
    print("=" * 50)
    print(f"🔑 API Key: {TELNYX_API_KEY[:20]}...")
    
    setup = TelnyxSetup(TELNYX_API_KEY)
    
    # 1. Obtener números de teléfono
    print("\n📞 Obteniendo números de teléfono...")
    phone_numbers = await setup.get_phone_numbers()
    
    if not phone_numbers:
        print("❌ No se encontraron números de teléfono")
        print("💡 Ve a Telnyx Dashboard y compra un número de teléfono")
        return
    
    print(f"✅ Encontrados {len(phone_numbers)} números:")
    for number in phone_numbers:
        print(f"   - {number.get('phone_number', 'N/A')} (ID: {number.get('id', 'N/A')})")
    
    # 2. Configurar webhook para cada número
    webhook_url = "https://web-production-a2b02.up.railway.app/telnyx-webhook"
    
    print(f"\n🔗 Configurando webhook: {webhook_url}")
    
    for number in phone_numbers:
        phone_id = number.get('id')
        phone_number = number.get('phone_number')
        
        if phone_id:
            print(f"\n📞 Configurando {phone_number}...")
            success = await setup.configure_webhook(phone_id, webhook_url)
            
            if success:
                print(f"✅ {phone_number} configurado correctamente")
            else:
                print(f"❌ Error configurando {phone_number}")
    
    # 3. Probar webhook
    print(f"\n🧪 Probando webhook...")
    webhook_works = await setup.test_webhook(webhook_url)
    
    if webhook_works:
        print("✅ Todo configurado correctamente!")
        print("\n📋 Próximos pasos:")
        print("1. Llama a tu número de Telnyx")
        print("2. El bot debería contestar")
        print("3. Revisa los logs en Railway")
    else:
        print("❌ El webhook no funciona")
        print("💡 Verifica que la aplicación esté desplegada en Railway")

if __name__ == "__main__":
    asyncio.run(main()) 