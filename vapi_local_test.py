"""
Script local para probar Vapi con los datos proporcionados
Ejecutar en tu máquina local antes de integrar en Google Sites
"""

import requests
import json
import os
from datetime import datetime

# Datos de Vapi proporcionados
VAPI_PUBLIC_KEY = "f4ee5b98-ecad-46ed-9f08-a7a598d9652e"
VAPI_ASSISTANT_ID = "37431832-940f-4c90-b769-8f8e5bd1cc2a"
VAPI_PHONE_ID = "7f3b9939-d9e9-4dbe-afa7-491b6cdb0a49"
VAPI_BASE_URL = "https://api.vapi.ai"

def create_vapi_call(phone_number: str, metadata: dict = None):
    """Crear una llamada usando Vapi"""
    try:
        headers = {
            "Authorization": f"Bearer {VAPI_PUBLIC_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "phoneNumberId": VAPI_PHONE_ID,
            "assistantId": VAPI_ASSISTANT_ID,
            "customer": {
                "number": phone_number
            }
        }
        
        if metadata:
            payload["metadata"] = metadata
        
        print(f"🚀 Creando llamada a: {phone_number}")
        print(f"📋 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{VAPI_BASE_URL}/call",
            headers=headers,
            json=payload
        )
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Llamada creada exitosamente!")
            print(f"📞 Call ID: {result.get('id')}")
            print(f"📊 Estado: {result.get('status')}")
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"💥 Excepción: {str(e)}")
        return None

def get_call_status(call_id: str):
    """Obtener estado de una llamada"""
    try:
        headers = {
            "Authorization": f"Bearer {VAPI_PUBLIC_KEY}"
        }
        
        response = requests.get(
            f"{VAPI_BASE_URL}/call/{call_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error obteniendo estado: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"💥 Excepción: {str(e)}")
        return None

def test_vapi_connection():
    """Probar conexión con Vapi"""
    print("🔍 Probando conexión con Vapi...")
    
    headers = {
        "Authorization": f"Bearer {VAPI_PUBLIC_KEY}"
    }
    
    # Probar obtener información del assistant
    try:
        response = requests.get(
            f"{VAPI_BASE_URL}/assistant/{VAPI_ASSISTANT_ID}",
            headers=headers
        )
        
        if response.status_code == 200:
            assistant_info = response.json()
            print(f"✅ Assistant encontrado: {assistant_info.get('name', 'Sin nombre')}")
            print(f"📝 Modelo: {assistant_info.get('model', 'No especificado')}")
            print(f"🌍 Idioma: {assistant_info.get('language', 'No especificado')}")
            return True
        else:
            print(f"❌ Error obteniendo assistant: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Error de conexión: {str(e)}")
        return False

def main():
    """Función principal para probar Vapi"""
    print("🏥 CONSULTORIO MÉDICO - PRUEBA VAPI")
    print("=" * 50)
    
    # Probar conexión
    if not test_vapi_connection():
        print("❌ No se pudo conectar con Vapi. Verifica tus credenciales.")
        return
    
    print("\n✅ Conexión exitosa con Vapi!")
    
    # Solicitar número de teléfono
    while True:
        phone_number = input("\n📱 Ingresa el número de teléfono (con código de país, ej: +1234567890): ")
        
        if phone_number.startswith('+') and len(phone_number) >= 10:
            break
        else:
            print("❌ Formato incorrecto. Usa formato internacional (ej: +1234567890)")
    
    # Crear llamada
    metadata = {
        "source": "local_test",
        "timestamp": datetime.now().isoformat(),
        "test": True
    }
    
    result = create_vapi_call(phone_number, metadata)
    
    if result:
        call_id = result.get('id')
        print(f"\n🎉 ¡Llamada iniciada! Call ID: {call_id}")
        
        # Opcional: monitorear estado
        monitor = input("\n¿Quieres monitorear el estado de la llamada? (s/n): ").lower()
        if monitor == 's':
            print("\n📊 Monitoreando estado de la llamada...")
            print("Presiona Ctrl+C para detener")
            
            try:
                while True:
                    status = get_call_status(call_id)
                    if status:
                        print(f"📞 Estado: {status.get('status', 'Desconocido')}")
                        if status.get('status') in ['ended', 'failed']:
                            break
                    import time
                    time.sleep(5)  # Esperar 5 segundos
            except KeyboardInterrupt:
                print("\n⏹️ Monitoreo detenido")

if __name__ == "__main__":
    main() 