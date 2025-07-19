# Configuración de Telnyx Voice API

## 1. Configuración en Telnyx Dashboard

### 1.1 Obtener API Key
1. Ve a [Telnyx Dashboard](https://portal.telnyx.com/)
2. Navega a **API Keys** en el menú lateral
3. Crea una nueva API Key con permisos para:
   - Voice API
   - Webhooks
4. Copia la API Key

### 1.2 Configurar Números de Teléfono
1. Ve a **Phone Numbers** en el dashboard
2. Compra o configura un número de teléfono
3. Anota el número (ej: +526624920537)

### 1.3 Configurar Webhook
1. Ve a **Webhooks** en el dashboard
2. Crea un nuevo webhook con:
   - **URL**: `https://web-production-a2b02.up.railway.app/telnyx-webhook`
   - **Events**: Selecciona todos los eventos de voz
   - **HTTP Method**: POST

## 2. Configuración en Railway

### 2.1 Variables de Entorno
Agrega estas variables en Railway:

```bash
TELNYX_API_KEY=tu_api_key_aqui
TELNYX_WEBHOOK_SECRET=tu_webhook_secret_aqui
OPENAI_API_KEY=tu_openai_api_key_aqui
```

### 2.2 Configurar Webhook URL
En Telnyx, configura el webhook para apuntar a tu URL de Railway:
```
https://tu-app-name.up.railway.app/telnyx-webhook
```

## 3. Configuración de Llamadas

### 3.1 Llamadas Entrantes
Para recibir llamadas en tu número de Telnyx:

1. En el dashboard de Telnyx, ve a tu número de teléfono
2. Configura el **Webhook URL** para llamadas entrantes
3. Apunta a tu endpoint: `/telnyx-webhook`

### 3.2 Llamadas Salientes
Para hacer llamadas programáticamente:

```python
from setup_telnyx_voice import TelnyxVoiceManager

manager = TelnyxVoiceManager(TELNYX_API_KEY)
await manager.create_call("+526624920537", "+526622563607")
```

## 4. Eventos de Telnyx Voice API

### 4.1 Eventos Principales
- `call.initiated`: Llamada iniciada
- `call.answered`: Llamada contestada
- `call.speech.gathered`: Voz reconocida
- `call.hangup`: Llamada terminada

### 4.2 Estructura de Evento
```json
{
  "event_type": "call.speech.gathered",
  "data": {
    "call_control_id": "v3:call_control_id",
    "payload": {
      "speech": {
        "text": "Hola, necesito una cita"
      }
    }
  }
}
```

## 5. Funciones de Voz

### 5.1 Hablar Texto
```python
await manager.speak_text(call_control_id, "Hola, ¿en qué puedo ayudarle?")
```

### 5.2 Reconocimiento de Voz
```python
await manager.start_speech_recognition(call_control_id)
```

### 5.3 Colgar Llamada
```python
await manager.hangup_call(call_control_id)
```

## 6. Integración con OpenAI

### 6.1 Procesar Voz con AI
```python
# En el webhook
speech_text = event_data.get('data', {}).get('payload', {}).get('speech', {}).get('text', '')
response = await enhanced_ai_manager.generate_response(phone_number, speech_text)
await manager.speak_text(call_control_id, response)
```

## 7. Pruebas

### 7.1 Probar Webhook
```bash
curl -X POST https://tu-app.up.railway.app/telnyx-webhook \
  -H "Content-Type: application/json" \
  -d '{"event_type": "call.initiated", "data": {"call_control_id": "test"}}'
```

### 7.2 Probar Llamada
```bash
python setup_telnyx_voice.py
```

## 8. Troubleshooting

### 8.1 Errores Comunes
- **401 Unauthorized**: API Key incorrecta
- **404 Not Found**: URL de webhook incorrecta
- **500 Internal Server Error**: Error en el código del webhook

### 8.2 Logs
Revisa los logs en Railway para ver los eventos recibidos:
```
📞 Telnyx Voice API event recibido: {...}
🎯 Procesando evento: call.initiated
```

### 8.3 Verificar Configuración
```python
# Verificar API Key
print(f"API Key configurada: {'Sí' if TELNYX_API_KEY else 'No'}")

# Verificar webhook
print(f"Webhook URL: {WEBHOOK_URL}")
```

## 9. Limitaciones de Trial

### 9.1 Cuenta Trial
- Llamadas limitadas por mes
- Algunas funciones avanzadas no disponibles
- Reconocimiento de voz puede tener limitaciones

### 9.2 Alternativas
Para cuentas trial, usar menús DTMF en lugar de reconocimiento de voz:
```xml
<Gather input="dtmf" timeout="10" numDigits="1">
    <Say>Presione 1 para agendar cita</Say>
</Gather>
```

## 10. Próximos Pasos

1. **Configurar Google Calendar API** para agendar citas
2. **Implementar base de datos** para almacenar información de pacientes
3. **Agregar autenticación** para acceder a información sensible
4. **Implementar notificaciones** por SMS/email
5. **Crear dashboard** para administrar citas 