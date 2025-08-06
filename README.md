# AI Net Backend - Backend Completo y Funcional

## 🚀 Características

- ✅ **Autenticación JWT** - Login, registro y gestión de perfiles
- ✅ **Procesamiento REAL de videos** - Descarga de YouTube y generación automática de clips
- ✅ **Sistema de pagos** - Integración con Stripe para planes premium
- ✅ **Descargas seguras** - Descargar clips con autenticación
- ✅ **Panel de administración** - Estadísticas y gestión de usuarios
- ✅ **CORS configurado** - Conexión perfecta con frontend
- ✅ **Base de datos SQLite** - Fácil de configurar y usar
- ✅ **API RESTful** - Endpoints bien estructurados

## 🎬 Procesamiento Real de Videos

### Funcionalidades Implementadas:
- ✅ **Descarga automática** de videos de YouTube usando yt-dlp
- ✅ **Generación automática de clips** usando FFmpeg
- ✅ **Thumbnails automáticos** extraídos del video
- ✅ **Procesamiento asíncrono** - No bloquea la API
- ✅ **Estados de procesamiento** - Queued, downloading, processing, completed, failed
- ✅ **Estrategia inteligente** de generación de clips según duración del video

### Estrategia de Clips:
- **Videos cortos (≤1 minuto)**: 1 clip completo
- **Videos medianos (≤5 minutos)**: 3 clips de 30 segundos
- **Videos largos (>5 minutos)**: 5 clips de 60 segundos

## 📁 Estructura del Proyecto

```
backend-complete/
├── app/
│   ├── __init__.py          # Configuración principal con CORS
│   ├── models.py            # Modelos de base de datos
│   ├── auth/
│   │   └── routes.py        # Autenticación (login, registro, perfil)
│   ├── videos/
│   │   └── routes.py        # Procesamiento REAL de videos y clips
│   ├── payments/
│   │   └── routes.py        # Integración con Stripe
│   ├── downloads/
│   │   └── routes.py        # Descargas seguras
│   └── admin/
│       └── routes.py        # Panel de administración
├── requirements.txt         # Dependencias incluyendo yt-dlp
├── wsgi.py                 # Punto de entrada para Render
├── install-tools.sh        # Script para instalar FFmpeg y yt-dlp
├── env.example             # Variables de entorno
└── README.md               # Este archivo
```

## 🛠️ Instalación

### 1. Clonar y configurar

```bash
# Subir estos archivos a tu repositorio GitHub
# Luego clonar en Render
git clone https://github.com/Nunusita/AI-Net-Backend-Final.git
cd AI-Net-Backend-Final
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Instalar herramientas de procesamiento (IMPORTANTE)

```bash
# En el servidor (Render), ejecutar:
chmod +x install-tools.sh
./install-tools.sh
```

### 4. Configurar variables de entorno

En Render, agrega estas variables:

```
SECRET_KEY=tu-clave-secreta-muy-segura-aqui
JWT_SECRET_KEY=tu-clave-jwt-muy-segura-aqui
DATABASE_URL=sqlite:///app.db
```

## 🔧 Configuración en Render

### Variables de entorno requeridas:

```
SECRET_KEY=tu-clave-secreta-muy-segura-aqui
JWT_SECRET_KEY=tu-clave-jwt-muy-segura-aqui
DATABASE_URL=sqlite:///app.db
```

### Variables opcionales:

```
STRIPE_SECRET_KEY=sk_test_tu_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_tu_stripe_publishable_key
```

### Comandos de build (en Render):

```bash
# Build Command
pip install -r requirements.txt && chmod +x install-tools.sh && ./install-tools.sh

# Start Command
gunicorn wsgi:app
```

## 📡 Endpoints Disponibles

### Autenticación
- `POST /auth/register` - Registrar usuario
- `POST /auth/login` - Iniciar sesión
- `GET /auth/profile` - Obtener perfil
- `PUT /auth/profile` - Actualizar perfil

### Videos (PROCESAMIENTO REAL)
- `POST /videos/process` - Procesar video de YouTube (REAL)
- `GET /videos/status/<id>` - Ver estado del procesamiento
- `GET /videos/list` - Listar videos del usuario
- `GET /videos/<id>` - Obtener video específico
- `DELETE /videos/<id>` - Eliminar video
- `GET /videos/clips` - Obtener clips del usuario

### Pagos
- `GET /payments/plans` - Obtener planes disponibles
- `POST /payments/create-checkout-session` - Crear sesión de pago
- `GET /payments/subscription-status` - Estado de suscripción
- `POST /payments/cancel-subscription` - Cancelar suscripción

### Descargas
- `GET /downloads/clip/<id>` - Descargar clip específico
- `GET /downloads/video/<id>/all-clips` - Descargar todos los clips de un video
- `GET /downloads/user/all-clips` - Descargar todos los clips del usuario

### Administración
- `GET /admin/stats` - Estadísticas generales
- `GET /admin/users` - Listar usuarios
- `GET /admin/videos` - Listar todos los videos
- `GET /admin/user/<id>` - Detalles de usuario
- `PUT /admin/user/<id>/plan` - Actualizar plan de usuario

### Sistema
- `GET /` - Información de la API
- `GET /health` - Estado del backend
- `GET /api` - Endpoints disponibles

## 🧪 Probar la API

### 1. Verificar estado del backend:
```bash
curl https://tu-backend.onrender.com/health
```

### 2. Registrar usuario:
```bash
curl -X POST https://tu-backend.onrender.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

### 3. Procesar video REAL:
```bash
curl -X POST https://tu-backend.onrender.com/videos/process \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN" \
  -d '{"video_url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

### 4. Verificar estado del procesamiento:
```bash
curl -X GET https://tu-backend.onrender.com/videos/status/1 \
  -H "Authorization: Bearer TU_TOKEN"
```

## 🔗 Conexión con Frontend

El backend está configurado con CORS para permitir conexiones desde cualquier origen. Tu frontend debería poder conectarse sin problemas usando la URL de Render.

### Ejemplo de configuración en frontend:

```javascript
const API_BASE_URL = "https://tu-backend.onrender.com";

// Ejemplo de procesamiento de video
const response = await fetch(`${API_BASE_URL}/videos/process`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    video_url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
  })
});

// Verificar estado del procesamiento
const statusResponse = await fetch(`${API_BASE_URL}/videos/status/${videoId}`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

## 🎯 Características Especiales

### Límites por Plan
- **Plan Gratuito**: 2 videos por semana
- **Plan Semanal**: 5 videos por semana
- **Plan Mensual**: Videos ilimitados
- **Plan Anual**: Videos ilimitados + 50% descuento
- **Plan Vitalicio**: Acceso de por vida

### Procesamiento Real de Videos
- ✅ **Descarga automática** de YouTube
- ✅ **Generación automática de clips** con FFmpeg
- ✅ **Thumbnails automáticos**
- ✅ **Procesamiento asíncrono**
- ✅ **Estados de progreso**
- ✅ **Estrategia inteligente** según duración

### Seguridad
- ✅ Validación de emails
- ✅ Contraseñas hasheadas
- ✅ JWT tokens seguros
- ✅ Verificación de propiedad de recursos
- ✅ Límites por plan implementados

### Base de Datos
- ✅ SQLite para desarrollo fácil
- ✅ Modelos bien estructurados
- ✅ Relaciones entre tablas
- ✅ Cascade deletes configurado

## 🚀 Despliegue

1. **Sube todos los archivos** a tu repositorio GitHub
2. **Configura las variables de entorno** en Render
3. **Ejecuta el script de instalación** de herramientas
4. **Haz deploy** en Render
5. **Prueba la conexión** con tu frontend

## 📞 Soporte

Si tienes problemas:
1. Verifica que FFmpeg y yt-dlp estén instalados
2. Revisa los logs en Render
3. Prueba los endpoints con curl o Postman
4. Verifica que el frontend esté usando la URL correcta

¡Tu backend ahora procesa videos REALES de YouTube! 🎬 