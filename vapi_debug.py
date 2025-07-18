"""
Script de debug para diagnosticar problemas con Vapi
"""

import requests
import json

# Datos de Vapi proporcionados
VAPI_PUBLIC_KEY = "f4ee5b98-ecad-46ed-9f08-a7a598d9652e"
VAPI_ASSISTANT_ID = "37431832-940f-4c90-b769-8f8e5bd1cc2a"
VAPI_PHONE_ID = "7f3b9939-d9e9-4dbe-afa7-491b6cdb0a49"
VAPI_BASE_URL = "https://api.vapi.ai"

def test_api_key():
    """Probar diferentes formatos de autenticación"""
    print("🔍 DIAGNÓSTICO DE AUTENTICACIÓN VAPI")
    print("=" * 50)
    
    # Probar diferentes formatos de headers
    auth_formats = [
        ("Bearer", f"Bearer {VAPI_PUBLIC_KEY}"),
        ("Authorization", f"Authorization: Bearer {VAPI_PUBLIC_KEY}"),
        ("X-API-Key", f"X-API-Key: {VAPI_PUBLIC_KEY}"),
        ("API-Key", f"API-Key: {VAPI_PUBLIC_KEY}"),
        ("Token", f"Token: {VAPI_PUBLIC_KEY}")
    ]
    
    for auth_type, auth_header in auth_formats:
        print(f"\n🧪 Probando: {auth_type}")
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Añadir header de autenticación
        if auth_type == "Bearer":
            headers["Authorization"] = auth_header
        elif auth_type == "Authorization":
            headers["Authorization"] = auth_header.split(": ")[1]
        else:
            headers[auth_type] = auth_header.split(": ")[1]
        
        try:
            # Probar endpoint básico
            response = requests.get(
                f"{VAPI_BASE_URL}/assistant/{VAPI_ASSISTANT_ID}",
                headers=headers
            )
            
            print(f"📡 Status: {response.status_code}")
            print(f"📄 Headers enviados: {headers}")
            
            if response.status_code == 200:
                print("✅ ¡ÉXITO! Autenticación correcta")
                assistant_info = response.json()
                print(f"📋 Assistant: {assistant_info.get('name', 'Sin nombre')}")
                return True
            elif response.status_code == 401:
                print("❌ Error 401: No autorizado")
                print(f"📄 Respuesta: {response.text[:200]}")
            else:
                print(f"⚠️ Status inesperado: {response.status_code}")
                print(f"📄 Respuesta: {response.text[:200]}")
                
        except Exception as e:
            print(f"💥 Error: {str(e)}")
    
    return False

def test_public_endpoints():
    """Probar endpoints públicos de Vapi"""
    print("\n🌐 PROBANDO ENDPOINTS PÚBLICOS")
    print("=" * 50)
    
    try:
        # Probar si la API está disponible
        response = requests.get(f"{VAPI_BASE_URL}/health", timeout=10)
        print(f"🏥 Health check: {response.status_code}")
        
        # Probar documentación
        response = requests.get(f"{VAPI_BASE_URL}/docs", timeout=10)
        print(f"📚 Docs: {response.status_code}")
        
    except Exception as e:
        print(f"💥 Error conectando a Vapi: {str(e)}")

def check_credentials_format():
    """Verificar formato de las credenciales"""
    print("\n🔑 VERIFICANDO FORMATO DE CREDENCIALES")
    print("=" * 50)
    
    print(f"🔑 Public Key: {VAPI_PUBLIC_KEY}")
    print(f"   Longitud: {len(VAPI_PUBLIC_KEY)} caracteres")
    print(f"   Formato UUID: {len(VAPI_PUBLIC_KEY.split('-')) == 5}")
    
    print(f"\n🤖 Assistant ID: {VAPI_ASSISTANT_ID}")
    print(f"   Longitud: {len(VAPI_ASSISTANT_ID)} caracteres")
    print(f"   Formato UUID: {len(VAPI_ASSISTANT_ID.split('-')) == 5}")
    
    print(f"\n📞 Phone ID: {VAPI_PHONE_ID}")
    print(f"   Longitud: {len(VAPI_PHONE_ID)} caracteres")
    print(f"   Formato UUID: {len(VAPI_PHONE_ID.split('-')) == 5}")

def test_alternative_auth():
    """Probar métodos alternativos de autenticación"""
    print("\n🔄 PROBANDO MÉTODOS ALTERNATIVOS")
    print("=" * 50)
    
    # Probar sin autenticación (para ver qué error da)
    try:
        response = requests.get(
            f"{VAPI_BASE_URL}/assistant/{VAPI_ASSISTANT_ID}",
            headers={"Content-Type": "application/json"}
        )
        print(f"📡 Sin auth - Status: {response.status_code}")
        print(f"📄 Respuesta: {response.text[:200]}")
    except Exception as e:
        print(f"💥 Error: {str(e)}")
    
    # Probar con API key en query params
    try:
        response = requests.get(
            f"{VAPI_BASE_URL}/assistant/{VAPI_ASSISTANT_ID}?api_key={VAPI_PUBLIC_KEY}",
            headers={"Content-Type": "application/json"}
        )
        print(f"📡 Query param - Status: {response.status_code}")
    except Exception as e:
        print(f"💥 Error: {str(e)}")

def main():
    """Función principal de diagnóstico"""
    print("🏥 DIAGNÓSTICO COMPLETO VAPI")
    print("=" * 60)
    
    # Verificar formato de credenciales
    check_credentials_format()
    
    # Probar endpoints públicos
    test_public_endpoints()
    
    # Probar métodos alternativos
    test_alternative_auth()
    
    # Probar autenticación
    success = test_api_key()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ¡Problema resuelto! La autenticación funciona.")
    else:
        print("❌ PROBLEMAS IDENTIFICADOS:")
        print("1. La API key puede ser incorrecta")
        print("2. Puede ser una API key privada, no pública")
        print("3. El assistant puede no existir o no tener permisos")
        print("4. Puede necesitar una API key diferente")
        
        print("\n🔧 SOLUCIONES:")
        print("1. Verifica en https://vapi.ai que la API key sea correcta")
        print("2. Asegúrate de usar la API key pública, no privada")
        print("3. Verifica que el assistant 'Karla' exista y esté activo")
        print("4. Revisa los permisos de tu cuenta en Vapi")

if __name__ == "__main__":
    main() 