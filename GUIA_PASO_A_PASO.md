# 🚀 Guía Paso a Paso: Vapi + Google Sites

## 📋 Paso 1: Probar Vapi en tu Máquina Local

### 1.1 Instalar Dependencias
```bash
pip install requests
```

### 1.2 Ejecutar Script de Prueba
```bash
python vapi_local_test.py
```

**Qué hace este script:**
- ✅ Prueba la conexión con Vapi usando tus credenciales
- ✅ Valida que tu assistant "Karla" esté funcionando
- ✅ Permite crear llamadas de prueba
- ✅ Monitorea el estado de las llamadas

### 1.3 Probar con tu Número
1. Ejecuta el script
2. Ingresa tu número de teléfono (formato: +1234567890)
3. Confirma la llamada
4. Responde tu teléfono cuando suene
5. Habla con el asistente "Karla"

## 📋 Paso 2: Embeber en Google Sites

### 2.1 Preparar el Widget HTML
1. Abre el archivo `vapi_google_sites_widget.html`
2. Verifica que tus credenciales estén correctas:
   ```javascript
   const VAPI_PUBLIC_KEY = "f4ee5b98-ecad-46ed-9f08-a7a598d9652e";
   const VAPI_ASSISTANT_ID = "37431832-940f-4c90-b769-8f8e5bd1cc2a";
   const VAPI_PHONE_ID = "7f3b9939-d9e9-4dbe-afa7-491b6cdb0a49";
   ```

### 2.2 Subir a un Servidor Web
**Opción A: GitHub Pages (Gratis)**
1. Crea un repositorio en GitHub
2. Sube el archivo HTML
3. Activa GitHub Pages
4. Obtén la URL (ej: `https://tu-usuario.github.io/tu-repo/vapi_google_sites_widget.html`)

**Opción B: Netlify (Gratis)**
1. Ve a https://netlify.com
2. Arrastra el archivo HTML
3. Obtén la URL automáticamente

**Opción C: Vercel (Gratis)**
1. Ve a https://vercel.com
2. Sube el archivo HTML
3. Obtén la URL automáticamente

### 2.3 Embeber en Google Sites
1. Ve a tu sitio de Google Sites
2. Edita la página donde quieres el widget
3. Añade un elemento "Embed"
4. Pega la URL del archivo HTML
5. Ajusta el tamaño según necesites
6. Guarda y publica

## 📋 Paso 3: Configurar el Asistente "Karla"

### 3.1 Verificar Configuración en Vapi
1. Ve a https://vapi.ai
2. Inicia sesión
3. Ve a "Assistants"
4. Busca "Karla" (ID: 37431832-940f-4c90-b769-8f8e5bd1cc2a)

### 3.2 Configurar Base de Conocimiento
En el assistant "Karla", añade este prompt:

```
Eres Karla, la asistente virtual del consultorio del Dr. Xavier Xijemez Xifra, especialista en medicina interna.

INFORMACIÓN DEL CONSULTORIO:
- Doctor: Dr. Xavier Xijemez Xifra
- Especialidad: Medicina Interna
- Horarios: Lunes a viernes 8:00-18:00, Sábados 9:00-14:00
- Ubicación: [TU DIRECCIÓN]
- Experiencia: Más de 5,000 consultas realizadas

ESPECIALIDADES:
- Diabetes Mellitus tipo 1 y 2
- Hipertensión arterial
- Enfermedades cardiovasculares
- Problemas respiratorios
- Trastornos endocrinos
- Medicina preventiva

TU FUNCIÓN:
1. Saludar amablemente al paciente
2. Preguntar en qué puedo ayudarle
3. Responder preguntas sobre:
   - Horarios de atención
   - Ubicación del consultorio
   - Especialidades del doctor
   - Preparación para consultas
   - Información sobre citas
4. Para emergencias: recomendar acudir a servicios de urgencia
5. Ser profesional, empática y clara

Siempre identifícate como Karla y menciona que trabajas para el Dr. Xavier Xijemez Xifra.
```

### 3.3 Configurar Voz y Idioma
- **Voz**: Selecciona una voz en español
- **Idioma**: Spanish
- **Modelo**: GPT-4 o GPT-3.5

## 📋 Paso 4: Probar la Integración

### 4.1 Probar Localmente
```bash
# Ejecutar script de prueba
python vapi_local_test.py

# Ingresar tu número
# Confirmar llamada
# Responder teléfono
# Hablar con Karla
```

### 4.2 Probar en Google Sites
1. Ve a tu sitio web
2. Encuentra el widget
3. Ingresa un número de prueba
4. Presiona "Llamar al Asistente"
5. Verifica que recibas la llamada

## 🔧 Troubleshooting

### Error: "No se pudo conectar con Vapi"
- Verifica que las credenciales sean correctas
- Asegúrate de tener conexión a internet
- Revisa que el assistant "Karla" esté activo

### Error: "Formato incorrecto de teléfono"
- Usa formato internacional: +1234567890
- Incluye el código de país
- No uses espacios ni guiones

### Error: "No recibo la llamada"
- Verifica que el número esté correcto
- Asegúrate de que el teléfono esté encendido
- Revisa que no esté en modo avión
- Verifica que el assistant esté configurado

### Error en Google Sites: "No se puede cargar"
- Verifica que la URL del HTML sea correcta
- Asegúrate de que el archivo esté en un servidor web
- Revisa que no haya errores de CORS

## 📞 Flujo de Funcionamiento

1. **Usuario visita tu sitio web**
2. **Ve el widget del consultorio**
3. **Ingresa su número de teléfono**
4. **Presiona "Llamar al Asistente"**
5. **Recibe una llamada automática**
6. **Karla le saluda y le ayuda**
7. **Conversación natural en español**

## 🎯 Próximos Pasos

Una vez que esto funcione, puedes:

1. **Personalizar el diseño** del widget
2. **Añadir más información** del consultorio
3. **Integrar con tu API** para guardar datos
4. **Conectar con 8n8** para automatizaciones
5. **Añadir base de datos** para citas

## 💡 Tips

- **Prueba primero localmente** antes de embeber
- **Usa números de prueba** al principio
- **Monitorea las llamadas** en el dashboard de Vapi
- **Personaliza el prompt** según tus necesidades
- **Mantén las credenciales seguras**

¿Necesitas ayuda con algún paso específico? 