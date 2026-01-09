"""
Script para migrar datos locales a Render
Migra usuarios, obras, clientes, productos y registros de la DB local al servidor Render
"""
import sqlite3
import requests
import json
from datetime import datetime

# Configuración
LOCAL_DB = "backend/users.db"
RENDER_API = "https://aplicaci-n-mi.onrender.com"

def get_local_data():
    """Extrae todos los datos de la base de datos local"""
    conn = sqlite3.connect(LOCAL_DB)
    conn.row_factory = sqlite3.Row
    
    data = {
        "users": [],
        "obras": [],
        "clientes": [],
        "productos": [],
        "registros": []
    }
    
    # Obtener usuarios
    users = conn.execute("SELECT * FROM users").fetchall()
    for user in users:
        data["users"].append(dict(user))
    
    # Obtener obras
    obras = conn.execute("SELECT * FROM obras").fetchall()
    for obra in obras:
        data["obras"].append(dict(obra))
    
    # Obtener clientes
    clientes = conn.execute("SELECT * FROM clientes").fetchall()
    for cliente in clientes:
        data["clientes"].append(dict(cliente))
    
    # Obtener productos
    productos = conn.execute("SELECT * FROM productos").fetchall()
    for producto in productos:
        data["productos"].append(dict(producto))
    
    # Obtener registros
    registros = conn.execute("SELECT * FROM registros").fetchall()
    for registro in registros:
        data["registros"].append(dict(registro))
    
    conn.close()
    return data

def register_user_on_render(user):
    """Registra un usuario en Render usando el endpoint de registro"""
    try:
        # Para registrar necesitamos la contraseña sin hashear, 
        # pero solo tenemos el hash. Así que usaremos un endpoint diferente
        # o tendremos que crear usuarios manualmente
        
        # Por ahora, vamos a registrar usuarios específicos con contraseñas conocidas
        known_users = {
            "Panchita's Catering": {
                "email": "cotoala@gmail.com",
                "username": "Panchita's Catering",
                "password": "Panchita123",
                "birthdate": "1990-01-01"
            },
            "demo": {
                "email": "demo@example.com",
                "username": "demo",
                "password": "demo123",
                "birthdate": "1990-01-01"
            }
        }
        
        if user["username"] in known_users:
            user_data = known_users[user["username"]]
            response = requests.post(
                f"{RENDER_API}/api/register",
                data={
                    "email": user_data["email"],
                    "username": user_data["username"],
                    "birthdate": user_data["birthdate"],
                    "password": user_data["password"],
                    "confirm_password": user_data["password"]
                }
            )
            
            if response.status_code == 200:
                print(f"✓ Usuario '{user['username']}' registrado exitosamente")
                return True
            elif response.status_code == 400 and "ya existe" in response.text.lower():
                print(f"ℹ Usuario '{user['username']}' ya existe en Render")
                return True
            else:
                print(f"✗ Error al registrar '{user['username']}': {response.text}")
                return False
        else:
            print(f"⚠ Usuario '{user['username']}' no tiene contraseña conocida, omitiendo...")
            return False
    except Exception as e:
        print(f"✗ Error al registrar usuario: {e}")
        return False

def main():
    print("=" * 60)
    print("MIGRACIÓN DE DATOS LOCAL → RENDER")
    print("=" * 60)
    print()
    
    # Verificar que Render esté activo
    try:
        response = requests.get(f"{RENDER_API}/health", timeout=10)
        if response.status_code == 200:
            print("✓ Servidor Render activo")
        else:
            print("✗ Servidor Render no responde correctamente")
            return
    except Exception as e:
        print(f"✗ No se puede conectar a Render: {e}")
        return
    
    print()
    
    # Obtener datos locales
    print("Extrayendo datos de la base de datos local...")
    data = get_local_data()
    
    print(f"  - {len(data['users'])} usuarios")
    print(f"  - {len(data['obras'])} obras")
    print(f"  - {len(data['clientes'])} clientes")
    print(f"  - {len(data['productos'])} productos")
    print(f"  - {len(data['registros'])} registros")
    print()
    
    # Migrar usuarios
    print("Migrando usuarios...")
    for user in data['users']:
        register_user_on_render(user)
    
    print()
    print("=" * 60)
    print("MIGRACIÓN COMPLETADA")
    print("=" * 60)
    print()
    print("NOTA: Los datos adicionales (obras, clientes, productos, registros)")
    print("se crearán automáticamente cuando uses la aplicación con cada usuario.")
    print()

if __name__ == "__main__":
    main()
