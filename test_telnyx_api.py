#!/usr/bin/env python3
"""
Script para probar la API de Telnyx
"""

import os
import asyncio
import aiohttp
from dotenv import load_dotenv
import json

# Cargar variables de entorno
load_dotenv()

# API Key de Telnyx
TELNYX_API_KEY = "KEY019824F7A25307988B858E8EFE273309_bhA8IL88RjFzlsLFWcC6gS"

async def test_telnyx_api():
    """Probar la API de Telnyx"""
    print("🧪 Probando API de Telnyx...")
    print(f"🔑 API Key: {TELNYX_API_KEY[:20]}...")
    
    # URL base de Telnyx API
    base_url = "https://api.telnyx.com/v2"
    
    headers = {
        "Authorization": f"Bearer {TELNYX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        # Probar obtención de números de teléfono
        print("\n📞 Probando obtención de números de teléfono...")
        url = f"{base_url}/phone_numbers"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                print(f"📊 Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print("✅ API Key válida!")
                    print(f"📱 Números encontrados: {len(data.get('data', []))}")
                    
                    for number in data.get('data', []):
                        print(f"   - {number.get('phone_number', 'N/A')}")
                        
                elif response.status == 401:
                    print("❌ API Key inválida o sin permisos")
                else:
                    error_text = await response.text()
                    print(f"❌ Error: {error_text}")
                    
    except Exception as e:
        print(f"❌ Error conectando con Telnyx: {e}")

async def test_webhook_url():
    """Probar que el webhook URL funciona"""
    print("\n🌐 Probando webhook URL...")
    
    webhook_url = "https://web-production-a2b02.up.railway.app/telnyx-webhook"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Probar health check
            health_url = "https://web-production-a2b02.up.railway.app/health"
            async with session.get(health_url) as response:
                print(f"🏥 Health Check: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health: {data}")
                else:
                    print("❌ Health check falló")
            
            # Probar webhook
            test_data = {
                "test": "data",
                "event_type": "test"
            }
            
            async with session.post(webhook_url, json=test_data) as response:
                print(f"📞 Webhook Test: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Webhook: {data}")
                else:
                    error_text = await response.text()
                    print(f"❌ Webhook error: {error_text}")
                    
    except Exception as e:
        print(f"❌ Error probando webhook: {e}")

async def test_create_call():
    """Probar creación de llamada (solo si tienes números configurados)"""
    print("\n📞 Probando creación de llamada...")
    
    # Solo probar si tienes números configurados
    from_number = "+526624920537"  # Tu número de Telnyx
    to_number = "+526622563607"    # Número de destino
    
    url = "https://api.telnyx.com/v2/calls"
    
    headers = {
        "Authorization": f"Bearer {TELNYX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "from": from_number,
        "to": to_number,
        "webhook_url": "https://web-production-a2b02.up.railway.app/telnyx-webhook",
        "webhook_url_timeout": 30,
        "webhook_url_method": "POST"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                print(f"📞 Crear llamada: {response.status}")
                
                if response.status == 201:
                    data = await response.json()
                    print("✅ Llamada creada exitosamente!")
                    print(f"📊 Call Control ID: {data.get('data', {}).get('call_control_id', 'N/A')}")
                elif response.status == 400:
                    error_data = await response.json()
                    print(f"❌ Error en payload: {error_data}")
                elif response.status == 401:
                    print("❌ API Key inválida")
                else:
                    error_text = await response.text()
                    print(f"❌ Error: {error_text}")
                    
    except Exception as e:
        print(f"❌ Error creando llamada: {e}")

if __name__ == "__main__":
    print("🚀 Telnyx API Test")
    print("=" * 50)
    
    # Ejecutar pruebas
    asyncio.run(test_telnyx_api())
    asyncio.run(test_webhook_url())
    
    # Preguntar si quiere probar crear llamada
    print("\n" + "=" * 50)
    print("¿Quieres probar crear una llamada? (s/n): ", end="")
    
    # Por ahora, no crear llamada automáticamente
    print("Saltando prueba de llamada por seguridad")
    
    print("\n✅ Pruebas completadas!") 