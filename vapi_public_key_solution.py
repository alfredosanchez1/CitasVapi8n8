"""
Solución para usar API key pública de Vapi
Las API keys públicas tienen limitaciones de seguridad
"""

import requests
import json
from datetime import datetime

# Datos de Vapi proporcionados
VAPI_PUBLIC_KEY = "f4ee5b98-ecad-46ed-9f08-a7a598d9652e"
VAPI_ASSISTANT_ID = "37431832-940f-4c90-b769-8f8e5bd1cc2a"
VAPI_PHONE_ID = "7f3b9939-d9e9-4dbe-afa7-491b6cdb0a49"
VAPI_BASE_URL = "https://api.vapi.ai"

def test_public_key_limits():
    """Probar qué endpoints funcionan con API key pública"""
    print("🔍 PROBANDO LÍMITES DE API KEY PÚBLICA")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {VAPI_PUBLIC_KEY}",
        "Content-Type": "application/json"
    }
    
    # Endpoints que SÍ deberían funcionar con API key pública
    public_endpoints = [
        ("/call", "POST", "Crear llamada"),
        ("/call/{call_id}", "GET", "Obtener estado de llamada"),
        ("/call/{call_id}/transcript", "GET", "Obtener transcripción"),
    ]
    
    # Endpoints que NO funcionan con API key pública
    private_endpoints = [
        ("/assistant/{assistant_id}", "GET", "Obtener assistant"),
        ("/assistant", "GET", "Listar assistants"),
        ("/phone-number", "GET", "Listar números"),
    ]
    
    print("✅ ENDPOINTS PÚBLICOS (deberían funcionar):")
    for endpoint, method, description in public_endpoints:
        print(f"   {method} {endpoint} - {description}")
    
    print("\n❌ ENDPOINTS PRIVADOS (no funcionan con API key pública):")
    for endpoint, method, description in private_endpoints:
        print(f"   {method} {endpoint} - {description}")

def create_call_with_public_key(phone_number: str):
    """Crear llamada usando API key pública"""
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
            },
            "metadata": {
                "source": "public_key_test",
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

def get_call_status_public(call_id: str):
    """Obtener estado de llamada usando API key pública"""
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

def main():
    """Función principal para probar con API key pública"""
    print("🏥 CONSULTORIO MÉDICO - API KEY PÚBLICA")
    print("=" * 50)
    
    # Explicar limitaciones
    test_public_key_limits()
    
    print("\n" + "=" * 50)
    print("💡 IMPORTANTE: Las API keys públicas tienen limitaciones de seguridad")
    print("   - Solo pueden crear llamadas")
    print("   - Solo pueden obtener estado de llamadas específicas")
    print("   - NO pueden acceder a información de assistants o phone numbers")
    print("   - Esto es normal y esperado para seguridad")
    
    # Solicitar número de teléfono
    while True:
        phone_number = input("\n📱 Ingresa el número de teléfono (con código de país, ej: +1234567890): ")
        
        if phone_number.startswith('+') and len(phone_number) >= 10:
            break
        else:
            print("❌ Formato incorrecto. Usa formato internacional (ej: +1234567890)")
    
    # Crear llamada
    result = create_call_with_public_key(phone_number)
    
    if result:
        call_id = result.get('id')
        print(f"\n🎉 ¡Llamada iniciada! Call ID: {call_id}")
        
        # Monitorear estado
        monitor = input("\n¿Quieres monitorear el estado de la llamada? (s/n): ").lower()
        if monitor == 's':
            print("\n📊 Monitoreando estado de la llamada...")
            print("Presiona Ctrl+C para detener")
            
            try:
                while True:
                    status = get_call_status_public(call_id)
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