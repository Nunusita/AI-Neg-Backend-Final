# 🚀 Instrucciones para Subir el Backend a GitHub

## ✅ Archivos Listos

Todos los archivos del backend completo están listos en esta carpeta:

```
ai-net-backend-temp/
├── app/
│   ├── __init__.py          ✅ Configuración principal con CORS
│   ├── models.py            ✅ Modelos de base de datos
│   ├── auth/
│   │   ├── __init__.py      ✅
│   │   └── routes.py        ✅ Autenticación (login, registro, perfil)
│   ├── videos/
│   │   ├── __init__.py      ✅
│   │   └── routes.py        ✅ Procesamiento REAL de videos y clips
│   ├── payments/
│   │   ├── __init__.py      ✅
│   │   └── routes.py        ✅ Integración con Stripe
│   ├── downloads/
│   │   ├── __init__.py      ✅
│   │   └── routes.py        ✅ Descargas seguras
│   └── admin/
│       ├── __init__.py      ✅
│       └── routes.py        ✅ Panel de administración
├── requirements.txt         ✅ Dependencias incluyendo yt-dlp
├── wsgi.py                 ✅ Punto de entrada para Render
├── install-tools.sh        ✅ Script para instalar FFmpeg y yt-dlp
├── env.example             ✅ Variables de entorno
├── README.md               ✅ Documentación completa
└── INSTRUCCIONES.md        ✅ Este archivo
```

## 🎬 Procesamiento REAL de Videos

### ✅ Funcionalidades Implementadas:
- **Descarga automática** de videos de YouTube usando yt-dlp
- **Generación automática de clips** usando FFmpeg
- **Thumbnails automáticos** extraídos del video
- **Procesamiento asíncrono** - No bloquea la API
- **Estados de procesamiento** - Queued, downloading, processing, completed, failed
- **Estrategia inteligente** de generación de clips según duración del video

### 📊 Estrategia de Clips:
- **Videos cortos (≤1 minuto)**: 1 clip completo
- **Videos medianos (≤5 minutos)**: 3 clips de 30 segundos
- **Videos largos (>5 minutos)**: 5 clips de 60 segundos

## 📋 Pasos para Subir a GitHub

### 1. Ir a tu repositorio GitHub
Ve a: https://github.com/Nunusita/AI-Net-Backend-Final

### 2. Subir los archivos
Tienes dos opciones:

#### Opción A: Subir desde GitHub Web
1. Ve a tu repositorio en GitHub
2. Haz clic en "Add file" → "Upload files"
3. Arrastra todos los archivos de esta carpeta
4. Escribe un mensaje de commit: "Backend completo AI Net con procesamiento real de videos"
5. Haz clic en "Commit changes"

#### Opción B: Usar Git desde línea de comandos
```bash
# Navegar a la carpeta del backend
cd ai-net-backend-temp

# Inicializar git
git init

# Agregar todos los archivos
git add .

# Hacer commit
git commit -m "Backend completo AI Net - Procesamiento REAL de videos con FFmpeg y yt-dlp"

# Agregar el repositorio remoto
git remote add origin https://github.com/Nunusita/AI-Net-Backend-Final.git

# Subir los cambios
git push -u origin main
```

## 🔧 Configurar en Render

### 1. Variables de entorno requeridas:
En tu dashboard de Render, agrega estas variables:

```
SECRET_KEY=tu-clave-secreta-muy-segura-aqui
JWT_SECRET_KEY=tu-clave-jwt-muy-segura-aqui
DATABASE_URL=sqlite:///app.db
```

### 2. Variables opcionales:
```
STRIPE_SECRET_KEY=sk_test_tu_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_tu_stripe_publishable_key
```

### 3. Comandos de build (IMPORTANTE):
En Render, configura estos comandos:

**Build Command:**
```bash
pip install -r requirements.txt && chmod +x install-tools.sh && ./install-tools.sh
```

**Start Command:**
```bash
gunicorn wsgi:app
```

## 🚀 Hacer Deploy

1. Ve a tu dashboard de Render
2. Selecciona tu servicio del backend
3. Configura los comandos de build y start
4. Haz clic en "Manual Deploy" → "Deploy latest commit"
5. Espera a que termine el deploy

## 🧪 Probar la Conexión

Una vez que el deploy esté completo, ejecuta:

```bash
node test-backend-complete.js
```

## ✅ Verificar que Funciona

El backend debería responder correctamente a:
- `https://ai-net-backend-final.onrender.com/health`
- `https://ai-net-backend-final.onrender.com/`
- `https://ai-net-backend-final.onrender.com/api`

### Probar procesamiento REAL de videos:
```bash
# 1. Registrar usuario
curl -X POST https://ai-net-backend-final.onrender.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# 2. Hacer login
curl -X POST https://ai-net-backend-final.onrender.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# 3. Procesar video REAL
curl -X POST https://ai-net-backend-final.onrender.com/videos/process \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN" \
  -d '{"video_url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# 4. Verificar estado del procesamiento
curl -X GET https://ai-net-backend-final.onrender.com/videos/status/1 \
  -H "Authorization: Bearer TU_TOKEN"
```

## 🎯 Resultado Esperado

Una vez completado:
- ✅ Tu frontend se conectará sin problemas
- ✅ El componente BackendStatus mostrará "Backend conectado"
- ✅ Todas las funciones de autenticación funcionarán
- ✅ El procesamiento REAL de videos estará disponible
- ✅ Los clips se generarán automáticamente con FFmpeg
- ✅ El sistema de pagos estará configurado

## 🔧 Herramientas Instaladas

El script `install-tools.sh` instalará automáticamente:
- ✅ **FFmpeg** - Para procesamiento de video
- ✅ **yt-dlp** - Para descarga de videos de YouTube
- ✅ **Directorios necesarios** - uploads/videos, uploads/clips, uploads/thumbnails

## 📞 Si Tienes Problemas

1. Verifica que todos los archivos estén en GitHub
2. Asegúrate de que FFmpeg y yt-dlp estén instalados
3. Revisa los logs en Render
4. Verifica que las variables de entorno estén configuradas
5. Prueba los endpoints con curl o Postman
6. Verifica que el frontend esté usando la URL correcta

## 🎬 Nuevas Funcionalidades

### Endpoints de Video:
- `POST /videos/process` - Procesar video REAL de YouTube
- `GET /videos/status/<id>` - Ver estado del procesamiento
- `GET /videos/list` - Listar videos del usuario
- `GET /videos/<id>` - Obtener video específico con clips
- `DELETE /videos/<id>` - Eliminar video y archivos
- `GET /videos/clips` - Obtener clips del usuario

### Estados de Procesamiento:
- **queued** - Video en cola de procesamiento
- **downloading** - Descargando video de YouTube
- **processing** - Generando clips con FFmpeg
- **completed** - Video procesado exitosamente
- **failed** - Error en el procesamiento

¡Tu backend ahora procesa videos REALES de YouTube! 🎬 