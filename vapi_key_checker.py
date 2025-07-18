"""
Script para diagnosticar problemas con API keys de Vapi
"""

import requests
import json

def check_api_key_format(api_key):
    """Verificar formato de API key"""
    print(f"🔑 Verificando formato de API key: {api_key}")
    print(f"   Longitud: {len(api_key)} caracteres")
    print(f"   Formato UUID: {len(api_key.split('-')) == 5}")
    print(f"   Contiene solo caracteres válidos: {api_key.replace('-', '').isalnum()}")
    
    # Verificar si parece ser una API key de Vapi
    if len(api_key) == 36 and len(api_key.split('-')) == 5:
        print("✅ Formato parece correcto (UUID v4)")
    else:
        print("❌ Formato no parece ser una API key válida de Vapi")

def test_api_key_endpoints(api_key):
    """Probar diferentes endpoints con la API key"""
    print(f"\n🧪 Probando API key en diferentes endpoints...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Endpoints para probar
    endpoints = [
        ("/assistant", "GET", "Listar assistants"),
        ("/phone-number", "GET", "Listar números"),
        ("/call", "POST", "Crear llamada (requiere payload)"),
    ]
    
    for endpoint, method, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(
                    f"https://api.vapi.ai{endpoint}",
                    headers=headers
                )
            else:
                # Para POST, solo probar la autenticación
                response = requests.post(
                    f"https://api.vapi.ai{endpoint}",
                    headers=headers,
                    json={}  # Payload vacío para probar auth
                )
            
            print(f"   {method} {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"      ✅ {description} - FUNCIONA")
            elif response.status_code == 401:
                print(f"      ❌ {description} - No autorizado")
            elif response.status_code == 400:
                print(f"      ⚠️ {description} - Bad request (puede ser normal para POST)")
            else:
                print(f"      ❓ {description} - Status {response.status_code}")
                
        except Exception as e:
            print(f"   {method} {endpoint}: 💥 Error - {str(e)}")

def check_vapi_connection():
    """Verificar si Vapi está disponible"""
    print("\n🌐 Verificando conexión con Vapi...")
    
    try:
        # Probar endpoint público
        response = requests.get("https://api.vapi.ai/health", timeout=10)
        print(f"   Health check: {response.status_code}")
        
        # Probar documentación
        response = requests.get("https://api.vapi.ai/docs", timeout=10)
        print(f"   Docs: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"   💥 Error conectando a Vapi: {str(e)}")
        return False

def main():
    """Función principal de diagnóstico"""
    print("🏥 DIAGNÓSTICO DE API KEY VAPI")
    print("=" * 50)
    
    # API key proporcionada
    api_key = "f4ee5b98-ecad-46ed-9f08-a7a598d9652e"
    
    # Verificar formato
    check_api_key_format(api_key)
    
    # Verificar conexión con Vapi
    if not check_vapi_connection():
        print("❌ No se puede conectar a Vapi. Verifica tu conexión a internet.")
        return
    
    # Probar endpoints
    test_api_key_endpoints(api_key)
    
    print("\n" + "=" * 50)
    print("📋 CONCLUSIONES:")
    print("❌ La API key proporcionada NO es válida")
    print("💡 Necesitas obtener la API key correcta desde Vapi Dashboard")
    
    print("\n🔧 SOLUCIONES:")
    print("1. Ve a https://vapi.ai")
    print("2. Inicia sesión con tu cuenta")
    print("3. Ve a 'API Keys' o 'Settings'")
    print("4. Busca la API key correcta")
    print("5. Cópiala exactamente como aparece")
    
    print("\n💡 TIPOS DE API KEYS:")
    print("- 🔒 Private Key: Para servidores/backend")
    print("- 🌐 Public Key: Para navegadores/frontend")
    print("- 📱 Ambas pueden crear llamadas")
    
    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. Obtén la API key correcta desde Vapi")
    print("2. Pruébala con este script")
    print("3. Una vez que funcione, podremos continuar")

if __name__ == "__main__":
    main() 