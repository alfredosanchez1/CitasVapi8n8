"""
Script local usando API key privada (más seguro para pruebas)
"""

import requests
import json
from datetime import datetime

# Datos de Vapi (API key privada para uso local)
VAPI_PRIVATE_KEY = "f4ee5b98-ecad-46ed-9f08-a7a598d9652e"  # Esta parece ser privada
VAPI_ASSISTANT_ID = "37431832-940f-4c90-b769-8f8e5bd1cc2a"
VAPI_PHONE_ID = "7f3b9939-d9e9-4dbe-afa7-491b6cdb0a49"
VAPI_BASE_URL = "https://api.vapi.ai"

def test_private_key():
    """Probar con API key privada"""
    print("🔍 PROBANDO CON API KEY PRIVADA")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
        "Content-Type": "application/json"
    }
    
    # Probar obtener información del assistant
    try:
        response = requests.get(
            f"{VAPI_BASE_URL}/assistant/{VAPI_ASSISTANT_ID}",
            headers=headers
        )
        
        print(f"📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            assistant_info = response.json()
            print("✅ ¡API key privada funciona!")
            print(f"📋 Assistant: {assistant_info.get('name', 'Sin nombre')}")
            print(f"📝 Modelo: {assistant_info.get('model', 'No especificado')}")
            print(f"🌍 Idioma: {assistant_info.get('language', 'No especificado')}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        return False

def create_call_private(phone_number: str):
    """Crear llamada usando API key privada"""
    try:
        headers = {
            "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "phoneNumberId": VAPI_PHONE_ID,
            "assistantId": VAPI_ASSISTANT_ID,
            "customer": {
                "number": phone_number
            },
            "metadata": {
                "source": "private_key_local_test",
                "timestamp": datetime.now().isoformat()
            }
        }
        
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
            print(f"✅ ¡Llamada creada exitosamente!")
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

def get_call_status_private(call_id: str):
    """Obtener estado de llamada usando API key privada"""
    try:
        headers = {
            "Authorization": f"Bearer {VAPI_PRIVATE_KEY}"
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

def main():
    """Función principal"""
    print("🏥 CONSULTORIO MÉDICO - API KEY PRIVADA (LOCAL)")
    print("=" * 60)
    
    # Probar API key privada
    if not test_private_key():
        print("\n❌ La API key privada no funciona.")
        print("💡 Necesitas obtener la API key correcta desde Vapi Dashboard")
        return
    
    print("\n✅ API key privada funciona correctamente!")
    
    # Solicitar número de teléfono
    while True:
        phone_number = input("\n📱 Ingresa TU número de teléfono (donde recibirás la llamada): ")
        
        if phone_number.startswith('+') and len(phone_number) >= 10:
            break
        else:
            print("❌ Formato incorrecto. Usa formato internacional (ej: +526622563607)")
    
    # Crear llamada
    result = create_call_private(phone_number)
    
    if result:
        call_id = result.get('id')
        print(f"\n🎉 ¡Llamada iniciada! Call ID: {call_id}")
        print(f"📞 Recibirás una llamada en: {phone_number}")
        
        # Monitorear estado
        monitor = input("\n¿Quieres monitorear el estado de la llamada? (s/n): ").lower()
        if monitor == 's':
            print("\n📊 Monitoreando estado de la llamada...")
            print("Presiona Ctrl+C para detener")
            
            try:
                while True:
                    status = get_call_status_private(call_id)
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