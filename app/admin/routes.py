from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, Video, Clip
from .. import db
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

def is_admin(user_id):
    """Verificar si el usuario es administrador"""
    user = User.query.get(user_id)
    return user and user.email == 'admin@ai-net.com'

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Obtener estadísticas generales"""
    try:
        user_id = get_jwt_identity()
        
        if not is_admin(user_id):
            return jsonify({'error': 'Acceso denegado'}), 403
        
        # Estadísticas básicas
        total_users = User.query.count()
        total_videos = Video.query.count()
        total_clips = Clip.query.count()
        
        # Usuarios por plan
        users_by_plan = db.session.query(User.plan, db.func.count(User.id)).group_by(User.plan).all()
        plan_stats = {plan: count for plan, count in users_by_plan}
        
        # Videos por estado
        videos_by_status = db.session.query(Video.status, db.func.count(Video.id)).group_by(Video.status).all()
        status_stats = {status: count for status, count in videos_by_status}
        
        # Actividad reciente (últimos 7 días)
        week_ago = datetime.utcnow() - timedelta(days=7)
        new_users_week = User.query.filter(User.created_at >= week_ago).count()
        new_videos_week = Video.query.filter(Video.created_at >= week_ago).count()
        
        return jsonify({
            'total_users': total_users,
            'total_videos': total_videos,
            'total_clips': total_clips,
            'users_by_plan': plan_stats,
            'videos_by_status': status_stats,
            'activity_week': {
                'new_users': new_users_week,
                'new_videos': new_videos_week
            }
        }), 200
        
    except Exception as e:
        print(f"Error al obtener estadísticas: {str(e)}")
        return jsonify({'error': 'Error al obtener estadísticas'}), 500

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Obtener lista de usuarios"""
    try:
        user_id = get_jwt_identity()
        
        if not is_admin(user_id):
            return jsonify({'error': 'Acceso denegado'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        users = User.query.order_by(User.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        print(f"Error al obtener usuarios: {str(e)}")
        return jsonify({'error': 'Error al obtener usuarios'}), 500

@admin_bp.route('/videos', methods=['GET'])
@jwt_required()
def get_all_videos():
    """Obtener todos los videos"""
    try:
        user_id = get_jwt_identity()
        
        if not is_admin(user_id):
            return jsonify({'error': 'Acceso denegado'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        videos = Video.query.order_by(Video.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        videos_data = []
        for video in videos.items:
            video_data = video.to_dict()
            video_data['user_email'] = video.user.email if video.user else 'N/A'
            videos_data.append(video_data)
        
        return jsonify({
            'videos': videos_data,
            'total': videos.total,
            'pages': videos.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        print(f"Error al obtener videos: {str(e)}")
        return jsonify({'error': 'Error al obtener videos'}), 500

@admin_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_details(user_id):
    """Obtener detalles de un usuario específico"""
    try:
        admin_user_id = get_jwt_identity()
        
        if not is_admin(admin_user_id):
            return jsonify({'error': 'Acceso denegado'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        user_data = user.to_dict()
        user_data['videos'] = [video.to_dict() for video in user.videos]
        user_data['total_videos'] = len(user.videos)
        user_data['total_clips'] = sum(len(video.clips) for video in user.videos)
        
        return jsonify(user_data), 200
        
    except Exception as e:
        print(f"Error al obtener detalles del usuario: {str(e)}")
        return jsonify({'error': 'Error al obtener detalles del usuario'}), 500

@admin_bp.route('/user/<int:user_id>/plan', methods=['PUT'])
@jwt_required()
def update_user_plan(user_id):
    """Actualizar plan de un usuario"""
    try:
        admin_user_id = get_jwt_identity()
        
        if not is_admin(admin_user_id):
            return jsonify({'error': 'Acceso denegado'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        data = request.get_json()
        if not data or 'plan' not in data:
            return jsonify({'error': 'Plan requerido'}), 400
        
        new_plan = data['plan']
        valid_plans = ['free', 'weekly', 'monthly', 'yearly', 'lifetime']
        
        if new_plan not in valid_plans:
            return jsonify({'error': 'Plan inválido'}), 400
        
        user.plan = new_plan
        db.session.commit()
        
        return jsonify({
            'message': f'Plan actualizado a {new_plan}',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar plan: {str(e)}")
        return jsonify({'error': 'Error al actualizar plan'}), 500 