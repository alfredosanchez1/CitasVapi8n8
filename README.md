# Consultorio Médico - Integración Vapi + Python

Sistema de reserva de citas médicas usando Vapi para llamadas de voz y Python para el backend.

## 🏗️ Arquitectura

```
Usuario llama → Vapi → Servidor Python → Base de Datos/8n8 → Respuesta
```

## 🚀 Opciones de Despliegue

### 1. **Railway (Recomendado para empezar)**

1. **Crear cuenta en Railway**: https://railway.app
2. **Conectar GitHub**: Sube este código a tu repositorio
3. **Desplegar**: Railway detectará automáticamente que es Python
4. **Configurar variables**: Añade las variables de entorno

```bash
# En Railway Dashboard
VAPI_API_KEY=tu_api_key
VAPI_PHONE_NUMBER_ID=tu_phone_id
VAPI_ASSISTANT_ID=tu_assistant_id
```

### 2. **Render (Gratis)**

1. **Crear cuenta en Render**: https://render.com
2. **Nuevo Web Service**
3. **Conectar repositorio**
4. **Configurar**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3. **Heroku**

```bash
# Instalar Heroku CLI
heroku create tu-app-name
git push heroku main
heroku config:set VAPI_API_KEY=tu_api_key
```

### 4. **DigitalOcean App Platform**

1. **Crear cuenta en DigitalOcean**
2. **App Platform → Create App**
3. **Conectar repositorio**
4. **Configurar variables de entorno**

## 📋 Configuración

### 1. **Variables de Entorno**

Crea un archivo `.env` basado en `env_example.txt`:

```bash
VAPI_API_KEY=tu_api_key_de_vapi
VAPI_PHONE_NUMBER_ID=tu_phone_number_id
VAPI_ASSISTANT_ID=tu_assistant_id
```

### 2. **Configurar Vapi**

1. **Crear cuenta en Vapi**: https://vapi.ai
2. **Obtener API Key** desde el dashboard
3. **Crear Phone Number** (número de teléfono)
4. **Crear Assistant** con tu base de conocimiento
5. **Configurar Webhook URL**: `https://tu-dominio.com/vapi-webhook`

### 3. **Instalar Dependencias**

```bash
pip install -r requirements.txt
```

## 🏥 Funcionalidades

### Endpoints Disponibles

- `GET /` - Información del API
- `POST /create-call` - Iniciar llamada
- `POST /vapi-webhook` - Webhook de Vapi
- `GET /appointments` - Listar citas
- `GET /health` - Estado del servidor

### Funciones del Asistente

- `get_appointment_info` - Información de horarios y ubicación
- `schedule_appointment` - Reservar cita

## 🔧 Desarrollo Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python main.py

# O con uvicorn
uvicorn main:app --reload
```

## 🌐 URLs de Producción

Una vez desplegado, tu API estará disponible en:

- **Railway**: `https://tu-app.railway.app`
- **Render**: `https://tu-app.onrender.com`
- **Heroku**: `https://tu-app.herokuapp.com`

## 🔗 Integración con 8n8

Para conectar con 8n8, añade en tu workflow:

1. **HTTP Request Node** → Tu endpoint `/create-call`
2. **Webhook Node** → Para recibir datos de citas
3. **Database Node** → Para guardar citas

## 📞 Flujo de Llamada

1. **Usuario llama** al número configurado en Vapi
2. **Vapi conecta** con tu asistente
3. **Asistente procesa** la conversación
4. **Funciones llamadas** → Tu servidor Python
5. **Respuesta enviada** al usuario
6. **Datos guardados** en base de datos/8n8

## 🛠️ Próximos Pasos

1. **Configurar base de datos** (PostgreSQL/MySQL)
2. **Integrar con 8n8** para automatizaciones
3. **Añadir autenticación** para endpoints
4. **Implementar notificaciones** SMS/Email
5. **Dashboard web** para administrar citas

## 💰 Costos Estimados

- **Railway**: $5-20/mes
- **Render**: Gratis (tier básico)
- **Heroku**: $7/mes mínimo
- **Vapi**: $0.01-0.05 por minuto de llamada

## 🆘 Soporte

- **Documentación Vapi**: https://docs.vapi.ai
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Railway Docs**: https://docs.railway.app 