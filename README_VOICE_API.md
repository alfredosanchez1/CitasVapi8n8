# 🎤 Bot de Voz Inteligente para Consultorio Médico

## Descripción

Este proyecto implementa un bot de voz inteligente para un consultorio médico que:

- ✅ Recibe llamadas telefónicas
- ✅ Procesa voz del usuario con reconocimiento de voz
- ✅ Genera respuestas inteligentes usando OpenAI
- ✅ Maneja citas médicas
- ✅ Proporciona información del consultorio
- ✅ Integra con Google Calendar (próximamente)

## 🚀 Configuración Rápida

### 1. Configurar Telnyx

1. **Crear cuenta en Telnyx**:
   - Ve a [Telnyx](https://telnyx.com) y crea una cuenta
   - Verifica tu cuenta (necesario para números de teléfono)

2. **Obtener API Key**:
   - En el dashboard, ve a **API Keys**
   - Crea una nueva API Key con permisos de Voice API
   - Copia la API Key

3. **Comprar número de teléfono**:
   - Ve a **Phone Numbers**
   - Compra un número de teléfono
   - Anota el número (ej: +526624920537)

### 2. Configurar Railway

1. **Fork este repositorio** o clónalo localmente

2. **Conectar con Railway**:
   ```bash
   railway login
   railway init
   ```

3. **Configurar variables de entorno**:
   ```bash
   railway variables set TELNYX_API_KEY=tu_api_key_aqui
   railway variables set OPENAI_API_KEY=tu_openai_api_key_aqui
   railway variables set TELNYX_WEBHOOK_SECRET=tu_webhook_secret
   ```

4. **Deploy**:
   ```bash
   railway up
   ```

### 3. Configurar Webhook en Telnyx

1. **En el dashboard de Telnyx**:
   - Ve a tu número de teléfono
   - Configura **Webhook URL** para llamadas entrantes
   - URL: `https://tu-app-name.up.railway.app/telnyx-webhook`

2. **Configurar eventos**:
   - Selecciona todos los eventos de voz
   - Método: POST

## 📞 Cómo Funciona

### Flujo de Llamada

1. **Usuario llama** al número de Telnyx
2. **Telnyx envía webhook** a tu aplicación
3. **Aplicación procesa** el evento con Python
4. **AI genera respuesta** usando OpenAI
5. **Sistema habla** la respuesta al usuario
6. **Reconocimiento de voz** captura la respuesta del usuario
7. **Ciclo continúa** hasta que se cuelga

### Eventos Principales

- `call.initiated`: Llamada iniciada
- `call.answered`: Llamada contestada  
- `call.speech.gathered`: Voz reconocida
- `call.hangup`: Llamada terminada

## 🛠️ Archivos Principales

### `main_voice_ai.py`
- Webhook principal para eventos de Telnyx
- Manejo de reconocimiento de voz
- Integración con OpenAI
- Respuestas inteligentes

### `setup_telnyx_voice.py`
- Cliente para Telnyx Voice API
- Funciones para crear llamadas
- Manejo de estados de llamada

### `ai_conversation_enhanced.py`
- Gestor de conversaciones con OpenAI
- Base de conocimiento del consultorio
- Generación de respuestas contextuales

## 🧪 Pruebas

### Probar Webhook
```bash
curl -X POST https://tu-app.up.railway.app/telnyx-webhook \
  -H "Content-Type: application/json" \
  -d '{"event_type": "call.initiated", "data": {"call_control_id": "test"}}'
```

### Probar Llamada
```bash
python setup_telnyx_voice.py
```

### Probar Localmente
```bash
python main_voice_ai.py
```

## 📋 Funcionalidades

### ✅ Implementadas
- [x] Recepción de llamadas
- [x] Reconocimiento de voz (español)
- [x] Respuestas con AI (OpenAI)
- [x] Menús DTMF (para cuentas trial)
- [x] Base de conocimiento médica
- [x] Información del consultorio
- [x] Manejo de errores

### 🚧 En Desarrollo
- [ ] Integración con Google Calendar
- [ ] Base de datos de pacientes
- [ ] Notificaciones SMS/Email
- [ ] Dashboard administrativo
- [ ] Autenticación de usuarios

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Telnyx
TELNYX_API_KEY=tu_api_key
TELNYX_WEBHOOK_SECRET=tu_secret

# OpenAI
OPENAI_API_KEY=tu_openai_key

# Google Calendar (próximamente)
GOOGLE_CALENDAR_ID=tu_calendar_id
GOOGLE_CREDENTIALS_FILE=path/to/credentials.json
```

### Personalización
1. **Modificar base de conocimiento**: Edita `BaseDeConocimiento.txt`
2. **Cambiar información del doctor**: Edita `CurriculumDr.XavierXijemezXifra.txt`
3. **Ajustar prompts**: Modifica `ai_conversation_enhanced.py`

## 🐛 Troubleshooting

### Errores Comunes

**401 Unauthorized**
- Verificar que TELNYX_API_KEY esté configurada correctamente
- Verificar permisos de la API Key

**404 Not Found**
- Verificar que la URL del webhook sea correcta
- Verificar que la aplicación esté desplegada

**500 Internal Server Error**
- Revisar logs en Railway
- Verificar que todas las dependencias estén instaladas

### Logs Útiles
```bash
# Ver logs en Railway
railway logs

# Ver logs locales
python main_voice_ai.py
```

## 📞 Ejemplo de Conversación

```
Bot: ¡Hola! Bienvenido al Consultorio de la Dra. Dolores Remedios del Rincón. 
     Soy su asistente virtual. ¿En qué puedo ayudarle hoy?

Usuario: Necesito agendar una cita

Bot: Perfecto, le ayudo a agendar su cita. ¿Es primera consulta o consulta de seguimiento?

Usuario: Es primera consulta

Bot: Entiendo. Para la primera consulta necesitará traer: documento de identidad, 
     carnet de obra social, estudios médicos previos y lista de medicamentos actuales. 
     ¿Qué día le gustaría venir?

Usuario: El próximo lunes

Bot: Perfecto. Tengo disponible el lunes a las 10:00 AM. ¿Le parece bien ese horario?

Usuario: Sí, perfecto

Bot: Excelente. Su cita ha sido agendada para el lunes a las 10:00 AM. 
     Recuerde traer toda la documentación necesaria. ¿Algo más en lo que pueda ayudarle?
```

## 🔒 Seguridad

- Todas las API keys se almacenan como variables de entorno
- No se almacenan datos sensibles en el código
- Webhooks verifican autenticidad de Telnyx
- Logs no contienen información personal

## 📈 Escalabilidad

- Arquitectura serverless con Railway
- Manejo asíncrono de llamadas
- Base de conocimiento extensible
- Fácil integración con otros servicios

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature
3. Haz commit de tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico:
- Revisa la documentación de [Telnyx](https://developers.telnyx.com/)
- Consulta los logs en Railway
- Abre un issue en GitHub

---

**¡Listo para usar! 🎉**

Tu bot de voz inteligente está configurado y listo para recibir llamadas. 