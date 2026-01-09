"""
Script completo para migrar TODOS los datos de Panchita's Catering a Render
Migra: obras, clientes, productos y registros
"""
import sqlite3
import requests
import json
from datetime import datetime

# Configuración
LOCAL_DB = "backend/users.db"
RENDER_API = "https://aplicaci-n-mi.onrender.com"
USERNAME = "Panchita's Catering"

def get_user_id_local(username):
    """Obtiene el user_id del usuario en la DB local"""
    conn = sqlite3.connect(LOCAL_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row["id"] if row else None

def get_local_data(user_id):
    """Extrae todos los datos del usuario de la base de datos local"""
    conn = sqlite3.connect(LOCAL_DB)
    conn.row_factory = sqlite3.Row
    
    data = {
        "obras": [],
        "clientes": [],
        "productos": [],
        "registros": []
    }
    
    # Obtener obras
    obras = conn.execute("SELECT * FROM obras WHERE user_id = ?", (user_id,)).fetchall()
    for obra in obras:
        data["obras"].append(dict(obra))
    
    # Obtener clientes
    clientes = conn.execute("SELECT * FROM clientes WHERE user_id = ?", (user_id,)).fetchall()
    for cliente in clientes:
        data["clientes"].append(dict(cliente))
    
    # Obtener productos
    productos = conn.execute("SELECT * FROM productos WHERE user_id = ?", (user_id,)).fetchall()
    for producto in productos:
        data["productos"].append(dict(producto))
    
    # Obtener registros
    registros = conn.execute("SELECT * FROM registros WHERE user_id = ?", (user_id,)).fetchall()
    for registro in registros:
        data["registros"].append(dict(registro))
    
    conn.close()
    return data

def migrate_obras(obras):
    """Migra obras a Render"""
    print(f"\nMigrando {len(obras)} obras...")
    success = 0
    for obra in obras:
        try:
            response = requests.post(
                f"{RENDER_API}/api/obras",
                data={
                    "username": USERNAME,
                    "nombre": obra["nombre"],
                    "ubicacion": obra.get("ubicacion", ""),
                    "estado": obra.get("estado", "activa")
                }
            )
            if response.status_code == 200:
                success += 1
                print(f"  ✓ Obra '{obra['nombre']}'")
            else:
                print(f"  ✗ Error en obra '{obra['nombre']}': {response.text}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    print(f"  Total: {success}/{len(obras)} obras migradas")

def migrate_clientes(clientes):
    """Migra clientes a Render"""
    print(f"\nMigrando {len(clientes)} clientes...")
    success = 0
    for cliente in clientes:
        try:
            response = requests.post(
                f"{RENDER_API}/api/clientes",
                data={
                    "username": USERNAME,
                    "nombre": cliente["nombre"],
                    "cedula": cliente.get("cedula", ""),
                    "obra": cliente.get("obra", ""),
                    "estado": cliente.get("estado", "activo"),
                    "fecha": cliente.get("fecha", "")
                }
            )
            if response.status_code == 200:
                success += 1
                print(f"  ✓ Cliente '{cliente['nombre']}'")
            else:
                print(f"  ✗ Error en cliente '{cliente['nombre']}': {response.text}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    print(f"  Total: {success}/{len(clientes)} clientes migrados")

def migrate_productos(productos):
    """Migra productos a Render"""
    print(f"\nMigrando {len(productos)} productos...")
    success = 0
    for producto in productos:
        try:
            response = requests.post(
                f"{RENDER_API}/api/productos",
                data={
                    "username": USERNAME,
                    "nombre": producto["nombre"],
                    "precio": producto.get("precio", 0)
                }
            )
            if response.status_code == 200:
                success += 1
                print(f"  ✓ Producto '{producto['nombre']}'")
            else:
                print(f"  ✗ Error en producto '{producto['nombre']}': {response.text}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    print(f"  Total: {success}/{len(productos)} productos migrados")

def migrate_registros(registros):
    """Migra registros a Render"""
    print(f"\nMigrando {len(registros)} registros...")
    success = 0
    for registro in registros:
        try:
            # Preparar datos del registro
            data = {
                "username": USERNAME,
                "fecha": registro.get("fecha", ""),
                "obra": registro.get("obra", ""),
                "totalCantidad": registro.get("totalCantidad", 0),
                "totalCobrar": registro.get("totalCobrar", 0),
                "totalPagado": registro.get("totalPagado", 0),
                "status": registro.get("status", "pendiente")
            }
            
            # Agregar campos opcionales si existen
            if registro.get("clientesAdicionales"):
                data["clientesAdicionales"] = registro["clientesAdicionales"]
            if registro.get("detalles"):
                data["detalles"] = registro["detalles"]
            
            response = requests.post(
                f"{RENDER_API}/api/registros",
                data=data
            )
            if response.status_code == 200:
                success += 1
                print(f"  ✓ Registro {registro['id']} - {registro.get('fecha', 'sin fecha')}")
            else:
                print(f"  ✗ Error en registro {registro['id']}: {response.text}")
        except Exception as e:
            print(f"  ✗ Error en registro {registro.get('id', '?')}: {e}")
    print(f"  Total: {success}/{len(registros)} registros migrados")

def main():
    print("=" * 70)
    print(f"MIGRACIÓN COMPLETA DE DATOS: {USERNAME} → RENDER")
    print("=" * 70)
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
    
    # Obtener user_id local
    user_id = get_user_id_local(USERNAME)
    if not user_id:
        print(f"✗ Usuario '{USERNAME}' no encontrado en la base de datos local")
        return
    
    print(f"✓ Usuario encontrado (ID local: {user_id})")
    print()
    
    # Obtener datos locales
    print("Extrayendo datos de la base de datos local...")
    data = get_local_data(user_id)
    
    print(f"  - {len(data['obras'])} obras")
    print(f"  - {len(data['clientes'])} clientes")
    print(f"  - {len(data['productos'])} productos")
    print(f"  - {len(data['registros'])} registros")
    
    # Migrar cada tipo de dato
    migrate_obras(data["obras"])
    migrate_clientes(data["clientes"])
    migrate_productos(data["productos"])
    migrate_registros(data["registros"])
    
    print()
    print("=" * 70)
    print("MIGRACIÓN COMPLETADA")
    print("=" * 70)
    print()
    print("Ahora puedes acceder a https://aplicaci-n-mi.vercel.app")
    print(f"e iniciar sesión con el usuario: {USERNAME}")
    print()

if __name__ == "__main__":
    main()
