# 🚀 Guía de Integración Vapi + FastAPI en Render

## 📋 Pasos para Integrar con tu API FastAPI Existente

### 1. **Preparar tu Proyecto**

#### Añadir Dependencias
Añade a tu `requirements.txt`:
```txt
requests==2.31.0
python-dotenv==1.0.0
```

#### Copiar Archivos
1. Copia `fastapi_vapi_integration.py` a tu proyecto
2. Asegúrate de que esté en el mismo directorio que tu `main.py`

### 2. **Modificar tu main.py**

#### Opción A: Integración Simple
```python
from fastapi import FastAPI
from fastapi_vapi_integration import add_vapi_routes

app = FastAPI(title="Tu API")

# Añadir rutas de Vapi
add_vapi_routes(app)

# Tus rutas existentes aquí...
```

#### Opción B: Integración Completa
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_vapi_integration import add_vapi_routes
import os

app = FastAPI(
    title="Consultorio Médico API",
    description="API con integración Vapi",
    version="1.0.0"
)

# CORS si lo necesitas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Añadir rutas de Vapi
add_vapi_routes(app)

# Tus rutas existentes...
@app.get("/")
async def root():
    return {"message": "Tu API funcionando"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### 3. **Configurar Variables en Render**

Ve a tu dashboard de Render → Environment Variables:

```bash
VAPI_API_KEY=tu_api_key_de_vapi
VAPI_PHONE_NUMBER_ID=tu_phone_number_id
VAPI_ASSISTANT_ID=tu_assistant_id
N8N_WEBHOOK_URL=https://tu-instancia-8n8.com/webhook (opcional)
```

### 4. **Configurar Vapi**

#### Crear Cuenta en Vapi
1. Ve a https://vapi.ai
2. Crea una cuenta
3. Obtén tu API Key del dashboard

#### Crear Phone Number
1. Dashboard → Phone Numbers
2. "Create Phone Number"
3. Selecciona tu país/región
4. Copia el Phone Number ID

#### Crear Assistant
1. Dashboard → Assistants
2. "Create Assistant"
3. Configura:
   - **Name**: "Consultorio Dr. Xavier Xijemez Xifra"
   - **Model**: GPT-4 o GPT-3.5
   - **Voice**: Selecciona una voz en español
   - **Language**: Spanish

#### Configurar Base de Conocimiento
En tu Assistant, añade este prompt:

```
Eres el asistente virtual del consultorio del Dr. Xavier Xijemez Xifra, especialista en medicina interna.

Información del consultorio:
- Horarios: Lunes a viernes 8:00-18:00, Sábados 9:00-14:00
- Ubicación: [TU DIRECCIÓN]
- Especialidades: Diabetes, hipertensión, enfermedades cardiovasculares, problemas respiratorios, trastornos endocrinos

Tu trabajo es:
1. Responder preguntas sobre horarios, ubicación y servicios
2. Ayudar a programar citas médicas
3. Proporcionar información sobre preparación para consultas
4. Manejar consultas de emergencia apropiadamente

Siempre sé profesional, empático y claro. Para emergencias, recomienda acudir a servicios de urgencia.
```

#### Configurar Webhook
1. En tu Assistant → Settings
2. Webhook URL: `https://tu-app.onrender.com/vapi-webhook`
3. Guardar configuración

### 5. **Configurar Funciones en Vapi**

En tu Assistant, añade estas funciones:

#### Función: get_appointment_info
```json
{
  "name": "get_appointment_info",
  "description": "Obtener información de horarios, ubicación y preparación para consultas",
  "parameters": {}
}
```

#### Función: schedule_appointment
```json
{
  "name": "schedule_appointment",
  "description": "Programar una cita médica",
  "parameters": {
    "patient_name": {
      "type": "string",
      "description": "Nombre completo del paciente"
    },
    "phone": {
      "type": "string", 
      "description": "Número de teléfono del paciente"
    },
    "date": {
      "type": "string",
      "description": "Fecha de la cita (YYYY-MM-DD)"
    },
    "time": {
      "type": "string",
      "description": "Hora de la cita (HH:MM)"
    },
    "reason": {
      "type": "string",
      "description": "Motivo de la consulta"
    }
  }
}
```

#### Función: get_doctor_info
```json
{
  "name": "get_doctor_info",
  "description": "Obtener información del Dr. Xavier Xijemez Xifra",
  "parameters": {}
}
```

#### Función: check_availability
```json
{
  "name": "check_availability",
  "description": "Verificar disponibilidad de horarios",
  "parameters": {
    "date": {
      "type": "string",
      "description": "Fecha a verificar (YYYY-MM-DD)"
    },
    "time": {
      "type": "string",
      "description": "Hora específica a verificar (HH:MM)"
    }
  }
}
```

### 6. **Probar la Integración**

#### Probar Webhook
```bash
curl -X POST https://tu-app.onrender.com/vapi-webhook \
  -H "Content-Type: application/json" \
  -d '{"type": "test", "data": {}}'
```

#### Probar Crear Llamada
```bash
curl -X POST https://tu-app.onrender.com/create-call \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "patient_name": "Juan Pérez",
    "reason": "Consulta de rutina"
  }'
```

#### Probar Endpoints
```bash
# Estado del servidor
curl https://tu-app.onrender.com/health

# Información médica
curl https://tu-app.onrender.com/medical-info

# Lista de citas
curl https://tu-app.onrender.com/appointments
```

### 7. **Integrar con 8n8 (Opcional)**

#### Crear Workflow en 8n8
1. Nuevo workflow
2. Añadir "Webhook" node
3. Copiar URL del webhook
4. Añadir "HTTP Request" node para tu API
5. Configurar para recibir datos de citas

#### Configurar en tu API
La integración ya está incluida. Solo añade la variable:
```bash
N8N_WEBHOOK_URL=https://tu-instancia-8n8.com/webhook/citas
```

### 8. **Endpoints Disponibles**

Una vez integrado, tendrás estos endpoints:

- `POST /vapi-webhook` - Webhook de Vapi
- `POST /create-call` - Crear llamada
- `GET /call-status/{call_id}` - Estado de llamada
- `GET /appointments` - Listar citas
- `GET /medical-info` - Info del consultorio
- `GET /health` - Estado del servidor

### 9. **Flujo de Llamada**

1. **Usuario llama** al número de Vapi
2. **Vapi conecta** con tu asistente
3. **Asistente procesa** la conversación
4. **Función llamada** → Tu API FastAPI en Render
5. **API procesa** la solicitud
6. **Respuesta enviada** al usuario
7. **Datos guardados** (opcional con 8n8)

## 🔧 Troubleshooting

### Error: "VAPI_API_KEY no configurada"
- Verifica variables en Render
- Reinicia la aplicación después de añadir variables

### Error: "Failed to create call"
- Verifica API Key, Phone Number ID y Assistant ID
- Revisa logs de Render

### Webhook no recibe eventos
- Verifica URL del webhook en Vapi
- Asegúrate de que tu API esté funcionando
- Revisa logs de Render

### Error de CORS
- Añade middleware CORS si es necesario
- Verifica configuración de origins

## 📞 Próximos Pasos

1. **Configurar base de datos** para guardar citas
2. **Añadir autenticación** a endpoints sensibles
3. **Implementar notificaciones** SMS/Email
4. **Crear dashboard web** para administrar citas
5. **Añadir más funciones** al asistente

## 💡 Tips para FastAPI

- **Usa Pydantic models** para validación
- **Implementa logging** para debuggear
- **Usa async/await** para operaciones I/O
- **Configura CORS** si necesitas frontend
- **Usa variables de entorno** para configuración

¿Necesitas ayuda con algún paso específico? 