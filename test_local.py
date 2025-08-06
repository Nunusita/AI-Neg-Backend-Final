#!/usr/bin/env python3
"""
Script de prueba local para verificar que el backend funciona correctamente
"""

import os
import sys
import subprocess

def test_imports():
    """Probar que todas las importaciones funcionan"""
    print("🧪 Probando importaciones...")
    
    try:
        from app import create_app
        print("✅ Importación de app exitosa")
        
        from app.models import User, Video, Clip
        print("✅ Importación de modelos exitosa")
        
        from app.auth.routes import auth_bp
        print("✅ Importación de auth_bp exitosa")
        
        from app.videos.routes import videos_bp
        print("✅ Importación de videos_bp exitosa")
        
        from app.payments.routes import payments_bp
        print("✅ Importación de payments_bp exitosa")
        
        from app.downloads.routes import downloads_bp
        print("✅ Importación de downloads_bp exitosa")
        
        from app.admin.routes import admin_bp
        print("✅ Importación de admin_bp exitosa")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en importaciones: {str(e)}")
        return False

def test_app_creation():
    """Probar que la aplicación se crea correctamente"""
    print("\n🧪 Probando creación de aplicación...")
    
    try:
        from app import create_app
        
        # Configurar variables de entorno para pruebas
        os.environ['SECRET_KEY'] = 'test-secret-key'
        os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
        os.environ['DATABASE_URL'] = 'sqlite:///test.db'
        
        app = create_app()
        print("✅ Aplicación creada exitosamente")
        
        # Probar que las rutas están registradas
        with app.app_context():
            routes = [str(rule) for rule in app.url_map.iter_rules()]
            print(f"✅ Rutas registradas: {len(routes)} rutas encontradas")
            
            # Verificar rutas principales
            expected_routes = ['/', '/health', '/api', '/auth/', '/videos/', '/payments/', '/downloads/', '/admin/']
            for route in expected_routes:
                if any(route in r for r in routes):
                    print(f"✅ Ruta {route} encontrada")
                else:
                    print(f"⚠️  Ruta {route} no encontrada")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando aplicación: {str(e)}")
        return False

def test_dependencies():
    """Probar que las dependencias están instaladas"""
    print("\n🧪 Probando dependencias...")
    
    required_packages = [
        'flask', 'flask_cors', 'flask_jwt_extended', 'flask_sqlalchemy',
        'flask_migrate', 'stripe', 'requests', 'python_dotenv', 'gunicorn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} instalado")
        except ImportError:
            print(f"❌ {package} NO instalado")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Paquetes faltantes: {', '.join(missing_packages)}")
        print("💡 Ejecuta: pip install -r requirements.txt")
        return False
    
    return True

def test_tools():
    """Probar que las herramientas están disponibles"""
    print("\n🧪 Probando herramientas...")
    
    tools = ['ffmpeg', 'yt-dlp']
    missing_tools = []
    
    for tool in tools:
        try:
            result = subprocess.run([tool, '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ {tool} disponible")
            else:
                print(f"❌ {tool} no funciona correctamente")
                missing_tools.append(tool)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"❌ {tool} NO encontrado")
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"\n⚠️  Herramientas faltantes: {', '.join(missing_tools)}")
        print("💡 Ejecuta: chmod +x install-tools.sh && ./install-tools.sh")
        return False
    
    return True

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del backend...")
    print("=" * 50)
    
    tests = [
        test_dependencies,
        test_imports,
        test_app_creation,
        test_tools
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Resultados: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El backend está listo para Render.")
        return True
    else:
        print("❌ Algunas pruebas fallaron. Revisa los errores arriba.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 