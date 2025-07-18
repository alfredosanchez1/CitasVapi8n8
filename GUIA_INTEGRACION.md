# 🚀 Guía de Integración Vapi + API Existente en Render

## 📋 Pasos para Integrar Vapi con tu API Actual

### 1. **Preparar tu API en Render**

#### Añadir Dependencias
Añade estas dependencias a tu `requirements.txt`:

```txt
requests==2.31.0
python-dotenv==1.0.0
```

#### Configurar Variables de Entorno en Render
Ve a tu dashboard de Render → Environment Variables y añade:

```bash
VAPI_API_KEY=tu_api_key_de_vapi
VAPI_PHONE_NUMBER_ID=tu_phone_number_id
VAPI_ASSISTANT_ID=tu_assistant_id
```

### 2. **Añadir el Módulo de Vapi**

#### Opción A: Copiar archivos
1. Copia `vapi_integration.py` a tu proyecto
2. Añade los endpoints a tu API existente

#### Opción B: Integrar manualmente
Añade estas funciones a tu archivo principal:

```python
# Importar al inicio de tu archivo
import requests
import os
from datetime import datetime

# Configuración de Vapi
VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_PHONE_NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
VAPI_ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")
```

### 3. **Añadir Endpoints a tu API**

#### Para Flask:
```python
@app.route('/vapi-webhook', methods=['POST'])
def vapi_webhook():
    webhook_data = request.get_json()
    # Procesar webhook aquí
    return jsonify({"status": "ok"})

@app.route('/create-call', methods=['POST'])
def create_call():
    data = request.get_json()
    phone_number = data.get('phone_number')
    # Crear llamada aquí
    return jsonify({"status": "call_created"})
```

#### Para FastAPI:
```python
@app.post("/vapi-webhook")
async def vapi_webhook(request: Request):
    webhook_data = await request.json()
    # Procesar webhook aquí
    return {"status": "ok"}

@app.post("/create-call")
async def create_call(call_request: CallRequest):
    # Crear llamada aquí
    return {"status": "call_created"}
```

### 4. **Configurar Vapi**

#### Crear cuenta en Vapi:
1. Ve a https://vapi.ai
2. Crea una cuenta
3. Obtén tu API Key

#### Crear Phone Number:
1. Dashboard → Phone Numbers
2. Crear nuevo número
3. Copia el Phone Number ID

#### Crear Assistant:
1. Dashboard → Assistants
2. Crear nuevo asistente
3. Configura con tu base de conocimiento
4. Copia el Assistant ID

#### Configurar Webhook:
1. En tu Assistant → Settings
2. Webhook URL: `https://tu-app.onrender.com/vapi-webhook`
3. Guardar configuración

### 5. **Probar la Integración**

#### Probar Webhook:
```bash
curl -X POST https://tu-app.onrender.com/vapi-webhook \
  -H "Content-Type: application/json" \
  -d '{"type": "test", "data": {}}'
```

#### Probar Crear Llamada:
```bash
curl -X POST https://tu-app.onrender.com/create-call \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}'
```

### 6. **Configurar Funciones en Vapi**

En tu Assistant de Vapi, configura estas funciones:

```json
{
  "name": "get_appointment_info",
  "description": "Obtener información de horarios y ubicación",
  "parameters": {}
}
```

```json
{
  "name": "schedule_appointment",
  "description": "Programar una cita médica",
  "parameters": {
    "patient_name": "string",
    "phone": "string",
    "date": "string",
    "time": "string",
    "reason": "string"
  }
}
```

### 7. **Integrar con 8n8 (Opcional)**

#### Crear Webhook en 8n8:
1. Nuevo workflow en 8n8
2. Añadir "Webhook" node
3. Copiar URL del webhook
4. Añadir "HTTP Request" node para tu API

#### Configurar en tu API:
```python
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

def notify_8n8(appointment_data):
    if N8N_WEBHOOK_URL:
        requests.post(N8N_WEBHOOK_URL, json=appointment_data)
```

## 🔧 Troubleshooting

### Error: "VAPI_API_KEY no configurada"
- Verifica que la variable esté configurada en Render
- Reinicia tu aplicación después de añadir variables

### Error: "Failed to create call"
- Verifica que tu API Key sea correcta
- Asegúrate de que Phone Number ID y Assistant ID sean válidos

### Webhook no recibe eventos
- Verifica que la URL del webhook sea correcta
- Asegúrate de que tu API esté funcionando
- Revisa los logs de Render

## 📞 Flujo Completo

1. **Usuario llama** al número de Vapi
2. **Vapi conecta** con tu asistente
3. **Asistente procesa** la conversación
4. **Función llamada** → Tu API en Render
5. **API procesa** la solicitud
6. **Respuesta enviada** al usuario
7. **Datos guardados** (opcional con 8n8)

## 🎯 Próximos Pasos

1. **Configurar base de datos** para guardar citas
2. **Añadir autenticación** a los endpoints
3. **Implementar notificaciones** SMS/Email
4. **Crear dashboard** para administrar citas
5. **Añadir más funciones** al asistente

## 💡 Tips

- **Usa logging** para debuggear
- **Prueba localmente** antes de desplegar
- **Mantén backups** de tu configuración
- **Monitorea** el uso de Vapi para controlar costos

¿Necesitas ayuda con algún paso específico? 