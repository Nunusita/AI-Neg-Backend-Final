from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Video, Clip, User
from .. import db
import re
import os
import subprocess
import requests
from datetime import datetime, timedelta
import threading
import time
from urllib.parse import urlparse, parse_qs

videos_bp = Blueprint('videos', __name__)

def validate_youtube_url(url):
    """Validar URL de YouTube"""
    youtube_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in youtube_patterns:
        if re.match(pattern, url):
            return True
    return False

def extract_video_id(url):
    """Extraer ID del video de YouTube"""
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            return match.group(1)
    return None

def get_video_info(video_id):
    """Obtener información del video de YouTube usando yt-dlp"""
    try:
        cmd = [
            'yt-dlp',
            '--dump-json',
            f'https://www.youtube.com/watch?v={video_id}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            import json
            video_info = json.loads(result.stdout)
            return {
                'title': video_info.get('title', f'Video {video_id}'),
                'duration': video_info.get('duration', 0),
                'thumbnail': video_info.get('thumbnail', ''),
                'success': True
            }
        else:
            return {
                'title': f'Video {video_id}',
                'duration': 0,
                'thumbnail': '',
                'success': False,
                'error': result.stderr
            }
    except Exception as e:
        return {
            'title': f'Video {video_id}',
            'duration': 0,
            'thumbnail': '',
            'success': False,
            'error': str(e)
        }

def download_video(video_id, output_path):
    """Descargar video de YouTube usando yt-dlp"""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        cmd = [
            'yt-dlp',
            '-f', 'best[height<=720]',
            '-o', output_path,
            f'https://www.youtube.com/watch?v={video_id}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0 and os.path.exists(output_path):
            return True
        else:
            print(f"Error descargando video: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error en download_video: {str(e)}")
        return False

def generate_clips(video_path, video_id, video_duration, clips_dir):
    """Generar clips del video usando FFmpeg"""
    try:
        os.makedirs(clips_dir, exist_ok=True)
        clips = []
        
        # Estrategia de clips según duración
        if video_duration <= 60:  # ≤1 minuto
            num_clips = 1
            clip_duration = video_duration
        elif video_duration <= 300:  # ≤5 minutos
            num_clips = 3
            clip_duration = 30
        else:  # >5 minutos
            num_clips = 5
            clip_duration = 60
        
        for i in range(num_clips):
            start_time = i * (video_duration / num_clips)
            end_time = min(start_time + clip_duration, video_duration)
            
            clip_filename = f"clip_{video_id}_{i+1}.mp4"
            clip_path = os.path.join(clips_dir, clip_filename)
            
            # Generar clip con FFmpeg
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-ss', str(start_time),
                '-t', str(end_time - start_time),
                '-c', 'copy',
                '-y',
                clip_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(clip_path):
                clip = Clip(
                    file_path=clip_path,
                    duration=end_time - start_time,
                    start_time=start_time,
                    end_time=end_time,
                    title=f"Clip {i+1} - {video_id}"
                )
                clips.append(clip)
        
        return clips
    except Exception as e:
        print(f"Error generando clips: {str(e)}")
        return []

def generate_thumbnail(video_path, video_id, thumbnails_dir):
    """Generar thumbnail del video"""
    try:
        os.makedirs(thumbnails_dir, exist_ok=True)
        thumbnail_path = os.path.join(thumbnails_dir, f"thumb_{video_id}.jpg")
        
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-ss', '00:00:05',
            '-vframes', '1',
            '-y',
            thumbnail_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and os.path.exists(thumbnail_path):
            return thumbnail_path
        else:
            return None
    except Exception as e:
        print(f"Error generando thumbnail: {str(e)}")
        return None

def process_video_async(video_id, user_id, video_url):
    """Procesar video de forma asíncrona"""
    try:
        with db.app.app_context():
            video = Video.query.get(video_id)
            if not video:
                return
            
            # Actualizar estado a downloading
            video.status = 'downloading'
            db.session.commit()
            
            # Crear directorios
            uploads_dir = 'uploads'
            videos_dir = os.path.join(uploads_dir, 'videos')
            clips_dir = os.path.join(uploads_dir, 'clips')
            thumbnails_dir = os.path.join(uploads_dir, 'thumbnails')
            
            os.makedirs(videos_dir, exist_ok=True)
            os.makedirs(clips_dir, exist_ok=True)
            os.makedirs(thumbnails_dir, exist_ok=True)
            
            # Obtener información del video
            video_info = get_video_info(extract_video_id(video_url))
            video.title = video_info['title']
            video.status = 'processing'
            db.session.commit()
            
            # Descargar video
            video_filename = f"video_{video_id}.mp4"
            video_path = os.path.join(videos_dir, video_filename)
            
            if download_video(extract_video_id(video_url), video_path):
                # Generar clips
                clips = generate_clips(video_path, video_id, video_info['duration'], clips_dir)
                
                # Generar thumbnail
                thumbnail_path = generate_thumbnail(video_path, video_id, thumbnails_dir)
                
                # Guardar clips en base de datos
                for clip in clips:
                    clip.video_id = video_id
                    if thumbnail_path:
                        clip.thumbnail_path = thumbnail_path
                    db.session.add(clip)
                
                # Actualizar video
                video.status = 'completed'
                db.session.commit()
                
                print(f"Video {video_id} procesado exitosamente")
            else:
                video.status = 'failed'
                db.session.commit()
                print(f"Error procesando video {video_id}")
                
    except Exception as e:
        print(f"Error en process_video_async: {str(e)}")
        try:
            with db.app.app_context():
                video = Video.query.get(video_id)
                if video:
                    video.status = 'failed'
                    db.session.commit()
        except:
            pass

@videos_bp.route('/process', methods=['POST'])
@jwt_required()
def process_video():
    """Procesar video de YouTube"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('video_url'):
            return jsonify({'error': 'URL del video requerida'}), 400
        
        video_url = data['video_url']
        
        if not validate_youtube_url(video_url):
            return jsonify({'error': 'URL de YouTube inválida'}), 400
        
        # Verificar límites del plan
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Verificar límites semanales
        week_ago = datetime.utcnow() - timedelta(days=7)
        videos_this_week = Video.query.filter(
            Video.user_id == user_id,
            Video.created_at >= week_ago
        ).count()
        
        if user.plan == 'free' and videos_this_week >= 2:
            return jsonify({'error': 'Límite semanal alcanzado (2 videos)'}), 429
        elif user.plan == 'weekly' and videos_this_week >= 5:
            return jsonify({'error': 'Límite semanal alcanzado (5 videos)'}), 429
        
        # Crear video en base de datos
        video = Video(
            user_id=user_id,
            youtube_url=video_url,
            status='queued'
        )
        
        db.session.add(video)
        db.session.commit()
        
        # Iniciar procesamiento asíncrono
        thread = threading.Thread(
            target=process_video_async,
            args=(video.id, user_id, video_url)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': 'Video agregado a la cola de procesamiento',
            'video_id': video.id,
            'status': 'queued'
        }), 202
        
    except Exception as e:
        print(f"Error en process_video: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@videos_bp.route('/list', methods=['GET'])
@jwt_required()
def get_videos():
    """Obtener lista de videos del usuario"""
    try:
        user_id = get_jwt_identity()
        
        videos = Video.query.filter_by(user_id=user_id).order_by(Video.created_at.desc()).all()
        
        return jsonify({
            'videos': [video.to_dict() for video in videos]
        }), 200
        
    except Exception as e:
        print(f"Error en get_videos: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@videos_bp.route('/<int:video_id>', methods=['GET'])
@jwt_required()
def get_video(video_id):
    """Obtener video específico"""
    try:
        user_id = get_jwt_identity()
        
        video = Video.query.filter_by(id=video_id, user_id=user_id).first()
        
        if not video:
            return jsonify({'error': 'Video no encontrado'}), 404
        
        return jsonify({
            'video': video.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Error en get_video: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@videos_bp.route('/<int:video_id>', methods=['DELETE'])
@jwt_required()
def delete_video(video_id):
    """Eliminar video"""
    try:
        user_id = get_jwt_identity()
        
        video = Video.query.filter_by(id=video_id, user_id=user_id).first()
        
        if not video:
            return jsonify({'error': 'Video no encontrado'}), 404
        
        # Eliminar archivos físicos
        try:
            if video.clips:
                for clip in video.clips:
                    if clip.file_path and os.path.exists(clip.file_path):
                        os.remove(clip.file_path)
                    if clip.thumbnail_path and os.path.exists(clip.thumbnail_path):
                        os.remove(clip.thumbnail_path)
        except Exception as e:
            print(f"Error eliminando archivos: {str(e)}")
        
        # Eliminar de base de datos (cascade eliminará clips)
        db.session.delete(video)
        db.session.commit()
        
        return jsonify({
            'message': 'Video eliminado exitosamente'
        }), 200
        
    except Exception as e:
        print(f"Error en delete_video: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@videos_bp.route('/status/<int:video_id>', methods=['GET'])
@jwt_required()
def get_video_status(video_id):
    """Obtener estado del procesamiento del video"""
    try:
        user_id = get_jwt_identity()
        
        video = Video.query.filter_by(id=video_id, user_id=user_id).first()
        
        if not video:
            return jsonify({'error': 'Video no encontrado'}), 404
        
        response = {
            'video_id': video.id,
            'status': video.status,
            'title': video.title,
            'created_at': video.created_at.isoformat() if video.created_at else None
        }
        
        if video.status == 'completed':
            response['clips_count'] = len(video.clips)
            response['clips'] = [clip.to_dict() for clip in video.clips]
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error en get_video_status: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@videos_bp.route('/clips', methods=['GET'])
@jwt_required()
def get_clips():
    """Obtener todos los clips del usuario"""
    try:
        user_id = get_jwt_identity()
        
        clips = Clip.query.join(Video).filter(Video.user_id == user_id).all()
        
        return jsonify({
            'clips': [clip.to_dict() for clip in clips],
            'total': len(clips)
        }), 200
        
    except Exception as e:
        print(f"Error en get_clips: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500 