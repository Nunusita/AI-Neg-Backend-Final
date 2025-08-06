from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    
    # Configurar CORS para permitir todas las conexiones
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"]
        }
    })
    
    # Inicializar extensiones
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
    # Importar modelos
    from .models import User, Video, Clip
    
    # Registrar blueprints
    from .auth.routes import auth_bp
    from .videos.video_routes import videos_bp
    from .payments.routes import payments_bp
    from .downloads.routes import downloads_bp
    from .admin.routes import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(videos_bp, url_prefix='/videos')
    app.register_blueprint(payments_bp, url_prefix='/payments')
    app.register_blueprint(downloads_bp, url_prefix='/downloads')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Rutas básicas
    @app.route('/')
    def index():
        return jsonify({
            'message': 'AI Net Backend API',
            'status': 'running',
            'version': '1.0.0'
        })
    
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'ok',
            'message': 'Backend funcionando correctamente',
            'database': 'connected' if db.engine.pool.checkedin() > 0 else 'disconnected'
        })
    
    @app.route('/api')
    def api_info():
        return jsonify({
            'endpoints': {
                'auth': '/auth',
                'videos': '/videos',
                'payments': '/payments',
                'downloads': '/downloads',
                'admin': '/admin'
            },
            'status': 'active'
        })
    
    # Crear tablas en la primera petición
    with app.app_context():
        db.create_all()
    
    return app 