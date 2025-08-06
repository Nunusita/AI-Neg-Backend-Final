from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..models import User
from .. import db
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email y contraseña requeridos'}), 400

    email = data['email'].lower().strip()
    password = data['password']

    # Validar email
    if not validate_email(email):
        return jsonify({'message': 'Formato de email inválido'}), 400

    # Validar contraseña
    if len(password) < 6:
        return jsonify({'message': 'La contraseña debe tener al menos 6 caracteres'}), 400

    # Verificar si el usuario ya existe
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'El usuario ya existe'}), 400

    # Crear nuevo usuario
    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(email=email, password=hashed_password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        
        # Generar token
        token = create_access_token(identity=new_user.id)
        
        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'token': token,
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al registrar usuario'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email y contraseña requeridos'}), 400

    email = data['email'].lower().strip()
    password = data['password']

    # Buscar usuario
    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Credenciales inválidas'}), 401

    # Generar token
    token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'Login exitoso',
        'token': token,
        'user': user.to_dict()
    })

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    
    return jsonify({
        'user': user.to_dict()
    })

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    
    data = request.get_json()
    
    if data.get('email'):
        email = data['email'].lower().strip()
        if not validate_email(email):
            return jsonify({'message': 'Formato de email inválido'}), 400
        
        # Verificar si el email ya está en uso
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'message': 'El email ya está en uso'}), 400
        
        user.email = email
    
    if data.get('password'):
        password = data['password']
        if len(password) < 6:
            return jsonify({'message': 'La contraseña debe tener al menos 6 caracteres'}), 400
        
        user.password = generate_password_hash(password, method='sha256')
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Perfil actualizado exitosamente',
            'user': user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al actualizar perfil'}), 500 