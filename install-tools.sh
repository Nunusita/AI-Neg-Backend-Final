#!/bin/bash

# Script para instalar herramientas necesarias para el procesamiento de videos
echo "🔧 Instalando herramientas para procesamiento de videos..."

# Actualizar paquetes
sudo apt-get update

# Instalar FFmpeg
echo "📹 Instalando FFmpeg..."
sudo apt-get install -y ffmpeg

# Verificar instalación de FFmpeg
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg instalado correctamente"
    ffmpeg -version | head -n 1
else
    echo "❌ Error instalando FFmpeg"
    exit 1
fi

# Instalar yt-dlp
echo "📥 Instalando yt-dlp..."
pip install yt-dlp

# Verificar instalación de yt-dlp
if command -v yt-dlp &> /dev/null; then
    echo "✅ yt-dlp instalado correctamente"
    yt-dlp --version
else
    echo "❌ Error instalando yt-dlp"
    exit 1
fi

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p uploads/videos
mkdir -p uploads/clips
mkdir -p uploads/thumbnails

echo "✅ Todas las herramientas instaladas correctamente"
echo "🎬 El backend ahora puede procesar videos reales de YouTube" 