from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Clip, Video
import os

downloads_bp = Blueprint('downloads', __name__)

@downloads_bp.route('/clip/<int:clip_id>', methods=['GET'])
@jwt_required()
def download_clip(clip_id):
    """Descargar clip específico"""
    try:
        user_id = get_jwt_identity()
        
        # Verificar que el clip pertenece al usuario
        clip = Clip.query.join(Video).filter(
            Clip.id == clip_id,
            Video.user_id == user_id
        ).first()
        
        if not clip:
            return jsonify({'error': 'Clip no encontrado'}), 404
        
        # Por ahora retornamos información del clip
        # En producción aquí iría la lógica de descarga real
        return jsonify({
            'clip': clip.to_dict(),
            'download_url': f"/api/downloads/clip/{clip_id}/file",
            'message': 'Descarga disponible'
        }), 200
        
    except Exception as e:
        print(f"Error al descargar clip: {str(e)}")
        return jsonify({'error': 'Error al descargar clip'}), 500

@downloads_bp.route('/clip/<int:clip_id>/file', methods=['GET'])
@jwt_required()
def download_clip_file(clip_id):
    """Descargar archivo del clip"""
    try:
        user_id = get_jwt_identity()
        
        # Verificar que el clip pertenece al usuario
        clip = Clip.query.join(Video).filter(
            Clip.id == clip_id,
            Video.user_id == user_id
        ).first()
        
        if not clip:
            return jsonify({'error': 'Clip no encontrado'}), 404
        
        # Simular archivo de descarga
        # En producción aquí iría la lógica real de descarga
        return jsonify({
            'message': 'Descarga simulada',
            'clip_info': clip.to_dict(),
            'file_size': '2.5 MB',
            'format': 'MP4'
        }), 200
        
    except Exception as e:
        print(f"Error al descargar archivo: {str(e)}")
        return jsonify({'error': 'Error al descargar archivo'}), 500

@downloads_bp.route('/video/<int:video_id>/all-clips', methods=['GET'])
@jwt_required()
def download_all_clips(video_id):
    """Descargar todos los clips de un video"""
    try:
        user_id = get_jwt_identity()
        
        # Verificar que el video pertenece al usuario
        video = Video.query.filter_by(id=video_id, user_id=user_id).first()
        if not video:
            return jsonify({'error': 'Video no encontrado'}), 404
        
        clips = Clip.query.filter_by(video_id=video_id).all()
        
        return jsonify({
            'video': video.to_dict(),
            'clips': [clip.to_dict() for clip in clips],
            'total_clips': len(clips),
            'message': f'Descarga de {len(clips)} clips disponible'
        }), 200
        
    except Exception as e:
        print(f"Error al descargar clips: {str(e)}")
        return jsonify({'error': 'Error al descargar clips'}), 500

@downloads_bp.route('/user/all-clips', methods=['GET'])
@jwt_required()
def download_user_clips():
    """Descargar todos los clips del usuario"""
    try:
        user_id = get_jwt_identity()
        
        # Obtener todos los clips del usuario
        clips = Clip.query.join(Video).filter(Video.user_id == user_id).all()
        
        return jsonify({
            'total_clips': len(clips),
            'clips': [clip.to_dict() for clip in clips],
            'message': f'Descarga de {len(clips)} clips disponible'
        }), 200
        
    except Exception as e:
        print(f"Error al obtener clips del usuario: {str(e)}")
        return jsonify({'error': 'Error al obtener clips'}), 500 