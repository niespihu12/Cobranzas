"""
Test script para verificar la conexión con Google Apps Script
"""

import requests
import json

# URL del Google Apps Script
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwjTxqCoL2euA72zP6LFf0segsKw1EOtoe-3K883xcGIqcdyGDOcu1NWHT_cWvjAFqv/exec"

def test_connection():
    """Prueba la conexión con Google Apps Script"""
    try:
        print("🔄 Probando conexión con Google Apps Script...")
        print(f"URL: {APPS_SCRIPT_URL}")
        
        response = requests.get(APPS_SCRIPT_URL)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Conexión exitosa!")
            
            if isinstance(data, list) and len(data) > 0:
                print(f"📊 Registros: {len(data)}")
                print(f"📋 Columnas: {len(data[0].keys()) if data[0] else 0}")
                
                if data[0]:
                    print(f"🏷️ Campos: {list(data[0].keys())[:5]}...")
                    
                    print("\n📋 Todos los campos:")
                    for i, field in enumerate(data[0].keys(), 1):
                        print(f"{i:2d}. {field}")
                    
                    print(f"\n📈 Primer registro:")
                    print(json.dumps(data[0], indent=2, ensure_ascii=False))
                    
                return True
            else:
                print("❌ No se encontraron datos o formato incorrecto")
                print(f"Tipo de datos: {type(data)}")
                print(f"Contenido: {data}")
                return False
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()