# 🚀 Instrucciones de Deployment Manual

## Problema Actual
Railway CLI no está funcionando en el terminal. Vamos a hacer el deployment manualmente.

## 📋 Pasos para Deployment Manual

### Paso 1: Verificar Archivos
Asegúrate de que tengas estos archivos en tu proyecto:

✅ `main_simple_working.py` - Versión simplificada que funciona  
✅ `start.py` - Script de inicio actualizado  
✅ `requirements.txt` - Dependencias  
✅ `Dockerfile` - Configuración de Docker  
✅ `.dockerignore` - Archivos a ignorar  

### Paso 2: Hacer Commit y Push a GitHub

Si tienes acceso a Git, haz:

```bash
git add .
git commit -m "Add simple working version for deployment"
git push origin master
```

### Paso 3: Deployment desde Railway Dashboard

1. **Abre [Railway Dashboard](https://railway.app/dashboard)**
2. **Selecciona tu proyecto** "CitasVapi8n8"
3. **Ve a la pestaña "Deployments"**
4. **Haz clic en "Deploy" o "Redeploy"**

### Paso 4: Si Railway está conectado a GitHub

Si tu proyecto está conectado a GitHub:
1. **Haz push a GitHub** (paso 2)
2. **Railway se desplegará automáticamente**

### Paso 5: Verificar Variables de Entorno

En Railway Dashboard, ve a "Variables" y asegúrate de que tengas:

```bash
TELNYX_API_KEY=tu_api_key_aqui
OPENAI_API_KEY=tu_openai_api_key_aqui
TELNYX_WEBHOOK_SECRET=tu_webhook_secret
```

### Paso 6: Verificar Deployment

Una vez desplegado, verifica:

1. **Health Check**: `https://tu-app.up.railway.app/health`
2. **Test Endpoint**: `https://tu-app.up.railway.app/test`
3. **Webhook**: `https://tu-app.up.railway.app/telnyx-webhook`

## 🔧 Alternativa: Usar Render.com

Si Railway sigue sin funcionar, puedes usar Render.com:

### Paso 1: Crear cuenta en Render
1. Ve a [Render.com](https://render.com)
2. Crea una cuenta gratuita

### Paso 2: Conectar GitHub
1. Conecta tu repositorio de GitHub
2. Selecciona el repositorio "CitasVapi8n8"

### Paso 3: Configurar Servicio
1. **Tipo**: Web Service
2. **Runtime**: Python 3
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `python start.py`

### Paso 4: Variables de Entorno
Agrega las mismas variables que en Railway.

## 🧪 Probar el Deployment

### Opción 1: Probar Health Check
```bash
curl https://tu-app.up.railway.app/health
```

### Opción 2: Probar Webhook
```bash
curl -X POST https://tu-app.up.railway.app/telnyx-webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### Opción 3: Probar desde navegador
Ve a: `https://tu-app.up.railway.app/health`

## 📞 Configurar Telnyx

Una vez que el deployment funcione:

1. **Ve a [Telnyx Dashboard](https://portal.telnyx.com/)**
2. **Selecciona tu número de teléfono**
3. **Configura Webhook URL**:
   ```
   https://tu-app.up.railway.app/telnyx-webhook
   ```

## 🐛 Troubleshooting

### Error: "Build Failed"
- Verifica que `requirements.txt` esté actualizado
- Verifica que `Dockerfile` esté correcto
- Revisa los logs de build

### Error: "Health Check Failed"
- Verifica que el puerto sea correcto (usar `PORT` en lugar de puerto fijo)
- Verifica que la aplicación se inicie correctamente

### Error: "Webhook Not Found"
- Verifica que la URL del webhook sea correcta
- Verifica que la aplicación esté desplegada

## 📱 Próximos Pasos

Una vez que el deployment funcione:

1. **Configura Telnyx** con tu webhook URL
2. **Llama a tu número** de Telnyx
3. **Verifica que el bot conteste** correctamente
4. **Revisa los logs** para ver los eventos

## 🆘 Si Nada Funciona

Si ninguna de estas opciones funciona:

1. **Usa Heroku** como alternativa
2. **Usa DigitalOcean App Platform**
3. **Usa Google Cloud Run**
4. **Contacta soporte** de Railway

---

**¡Suerte con el deployment! 🚀** 