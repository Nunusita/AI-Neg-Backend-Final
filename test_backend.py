#!/usr/bin/env python3
"""
Script de prueba para verificar que el backend funciona correctamente
"""

import requests
import json
import sys

def test_backend(base_url):
    """Probar endpoints básicos del backend"""
    
    print("🧪 Probando backend en:", base_url)
    print("=" * 50)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check: OK")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check: FAILED ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Health check: ERROR - {str(e)}")
        return False
    
    # Test 2: API info
    try:
        response = requests.get(f"{base_url}/api")
        if response.status_code == 200:
            print("✅ API info: OK")
            print(f"   Endpoints disponibles: {list(response.json()['endpoints'].keys())}")
        else:
            print(f"❌ API info: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ API info: ERROR - {str(e)}")
    
    # Test 3: Plans endpoint
    try:
        response = requests.get(f"{base_url}/payments/plans")
        if response.status_code == 200:
            print("✅ Plans endpoint: OK")
            plans = response.json()['plans']
            print(f"   Planes disponibles: {list(plans.keys())}")
        else:
            print(f"❌ Plans endpoint: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ Plans endpoint: ERROR - {str(e)}")
    
    print("=" * 50)
    print("🎉 Pruebas básicas completadas")
    return True

if __name__ == "__main__":
    # URL del backend (cambiar por tu URL de Render)
    backend_url = "http://localhost:5000"  # Para pruebas locales
    
    if len(sys.argv) > 1:
        backend_url = sys.argv[1]
    
    success = test_backend(backend_url)
    
    if success:
        print("\n🚀 El backend está funcionando correctamente!")
        print("💡 Para probar con tu URL de Render, ejecuta:")
        print(f"   python test_backend.py https://tu-backend.onrender.com")
    else:
        print("\n❌ El backend tiene problemas. Revisa los logs.")
        sys.exit(1) 