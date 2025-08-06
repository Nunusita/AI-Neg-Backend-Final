#!/usr/bin/env python3
"""
Script de verificación final para el despliegue en Render
"""

import os
import sys
import subprocess

def check_file_encoding(file_path):
    """Verificar que un archivo no tenga caracteres nulos"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if '\x00' in content:
                return False, f"Caracteres nulos encontrados en {file_path}"
            return True, f"Archivo {file_path} está limpio"
    except Exception as e:
        return False, f"Error leyendo {file_path}: {str(e)}"

def check_python_syntax(file_path):
    """Verificar sintaxis de Python"""
    try:
        result = subprocess.run([sys.executable, '-m', 'py_compile', file_path], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return True, f"Sintaxis correcta en {file_path}"
        else:
            return False, f"Error de sintaxis en {file_path}: {result.stderr}"
    except Exception as e:
        return False, f"Error verificando sintaxis de {file_path}: {str(e)}"

def main():
    """Función principal de verificación"""
    print("🔍 Verificación final del backend para Render")
    print("=" * 60)
    
    # Archivos críticos a verificar
    critical_files = [
        'wsgi.py',
        'app/__init__.py',
        'app/models.py',
        'app/auth/routes.py',
        'app/videos/video_routes.py',
        'app/payments/routes.py',
        'app/downloads/routes.py',
        'app/admin/routes.py'
    ]
    
    all_good = True
    
    # Verificar codificación y sintaxis
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"\n📁 Verificando {file_path}...")
            
            # Verificar codificación
            encoding_ok, encoding_msg = check_file_encoding(file_path)
            if encoding_ok:
                print(f"  ✅ {encoding_msg}")
            else:
                print(f"  ❌ {encoding_msg}")
                all_good = False
            
            # Verificar sintaxis
            syntax_ok, syntax_msg = check_python_syntax(file_path)
            if syntax_ok:
                print(f"  ✅ {syntax_msg}")
            else:
                print(f"  ❌ {syntax_msg}")
                all_good = False
        else:
            print(f"\n❌ Archivo no encontrado: {file_path}")
            all_good = False
    
    # Verificar archivos de configuración
    config_files = [
        'requirements.txt',
        'runtime.txt',
        'Procfile',
        'render.yaml',
        '.gitignore'
    ]
    
    print(f"\n📋 Verificando archivos de configuración...")
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"  ✅ {config_file} presente")
        else:
            print(f"  ❌ {config_file} faltante")
            all_good = False
    
    # Verificar estructura de directorios
    print(f"\n📁 Verificando estructura de directorios...")
    required_dirs = [
        'app',
        'app/auth',
        'app/videos', 
        'app/payments',
        'app/downloads',
        'app/admin'
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            print(f"  ✅ {dir_path}/ presente")
        else:
            print(f"  ❌ {dir_path}/ faltante")
            all_good = False
    
    # Resultado final
    print("\n" + "=" * 60)
    if all_good:
        print("🎉 ¡VERIFICACIÓN EXITOSA!")
        print("✅ Tu backend está listo para ser desplegado en Render")
        print("\n📋 Próximos pasos:")
        print("1. Sube los cambios a GitHub: git push origin main")
        print("2. Ve a Render.com y conecta tu repositorio")
        print("3. Render detectará automáticamente el render.yaml")
        print("4. ¡Tu backend estará funcionando en minutos!")
        return True
    else:
        print("❌ VERIFICACIÓN FALLIDA")
        print("⚠️  Hay problemas que necesitan ser corregidos antes del despliegue")
        print("\n💡 Revisa los errores arriba y corrígelos")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 