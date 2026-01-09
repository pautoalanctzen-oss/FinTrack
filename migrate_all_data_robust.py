"""
Script robusto para migrar TODOS los datos de Panchita's Catering a Render
Con manejo de errores y reintentos
"""
import sqlite3
import requests
import json
import time
from datetime import datetime

# Configuración
LOCAL_DB = "backend/users.db"
RENDER_API = "https://aplicaci-n-mi.onrender.com"
USERNAME = "Panchita's Catering"
REQUEST_TIMEOUT = 30
RETRY_COUNT = 3
RETRY_DELAY = 2

def wake_server():
    """Despierta el servidor de Render"""
    print("Despertando servidor de Render...")
    for attempt in range(5):
        try:
            response = requests.get(f"{RENDER_API}/health", timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                print(f"✓ Servidor activo\n")
                time.sleep(1)
                return True
        except:
            pass
        if attempt < 4:
            print(f"  Intento {attempt+1}/5, esperando...")
            time.sleep(5)
    print("✗ No se pudo conectar al servidor")
    return False

def get_local_data():
    """Extrae todos los datos del usuario de la DB local"""
    conn = sqlite3.connect(LOCAL_DB)
    conn.row_factory = sqlite3.Row
    
    # Obtener user_id
    cursor = conn.execute("SELECT id FROM users WHERE username = ?", (USERNAME,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return None
    
    user_id = user["id"]
    
    data = {
        "obras": [dict(row) for row in conn.execute("SELECT * FROM obras WHERE user_id = ? ORDER BY id", (user_id,))],
        "clientes": [dict(row) for row in conn.execute("SELECT * FROM clientes WHERE user_id = ? ORDER BY id", (user_id,))],
        "productos": [dict(row) for row in conn.execute("SELECT * FROM productos WHERE user_id = ? ORDER BY id", (user_id,))],
        "registros": [dict(row) for row in conn.execute("SELECT * FROM registros WHERE user_id = ? ORDER BY id", (user_id,))]
    }
    
    conn.close()
    return data

def post_with_retry(endpoint, data, item_name=""):
    """Realiza un POST con reintentos"""
    for attempt in range(RETRY_COUNT):
        try:
            response = requests.post(
                f"{RENDER_API}{endpoint}",
                data=data,
                timeout=REQUEST_TIMEOUT
            )
            if response.status_code == 200:
                return True
            elif response.status_code == 400 and "ya existe" in response.text.lower():
                return True  # Item ya existe, considerar como éxito
            else:
                if attempt < RETRY_COUNT - 1:
                    time.sleep(RETRY_DELAY)
        except Exception as e:
            if attempt < RETRY_COUNT - 1:
                time.sleep(RETRY_DELAY)
    return False

def migrate_obras(obras):
    """Migra obras a Render"""
    print(f"\n📋 Migrando {len(obras)} obras...")
    success = 0
    for i, obra in enumerate(obras, 1):
        data = {
            "username": USERNAME,
            "nombre": obra["nombre"],
            "ubicacion": obra.get("ubicacion", ""),
            "estado": obra.get("estado", "activa")
        }
        if post_with_retry("/api/obras", data, obra["nombre"]):
            success += 1
            print(f"  ✓ [{i}/{len(obras)}] {obra['nombre']}")
        else:
            print(f"  ✗ [{i}/{len(obras)}] {obra['nombre']}")
        time.sleep(0.3)
    
    print(f"  📊 Total: {success}/{len(obras)} obras migradas")
    return success == len(obras)

def migrate_clientes(clientes):
    """Migra clientes a Render"""
    print(f"\n👥 Migrando {len(clientes)} clientes...")
    success = 0
    for i, cliente in enumerate(clientes, 1):
        data = {
            "username": USERNAME,
            "nombre": cliente["nombre"],
            "cedula": cliente.get("cedula", ""),
            "obra": cliente.get("obra", ""),
            "estado": cliente.get("estado", "activo"),
            "fecha": cliente.get("fecha", "")
        }
        if post_with_retry("/api/clientes", data, cliente["nombre"]):
            success += 1
            if i % 5 == 0:
                print(f"  ✓ [{i}/{len(clientes)}] Procesados...")
        else:
            print(f"  ✗ [{i}/{len(clientes)}] {cliente['nombre']}")
        time.sleep(0.2)
    
    print(f"  📊 Total: {success}/{len(clientes)} clientes migrados")
    return success == len(clientes)

def migrate_productos(productos):
    """Migra productos a Render"""
    print(f"\n📦 Migrando {len(productos)} productos...")
    success = 0
    for i, producto in enumerate(productos, 1):
        data = {
            "username": USERNAME,
            "nombre": producto["nombre"],
            "precio": producto.get("precio", 0)
        }
        if post_with_retry("/api/productos", data, producto["nombre"]):
            success += 1
            print(f"  ✓ [{i}/{len(productos)}] {producto['nombre']}")
        else:
            print(f"  ✗ [{i}/{len(productos)}] {producto['nombre']}")
        time.sleep(0.2)
    
    print(f"  📊 Total: {success}/{len(productos)} productos migrados")
    return success == len(productos)

def migrate_registros(registros):
    """Migra registros a Render"""
    print(f"\n📝 Migrando {len(registros)} registros...")
    success = 0
    for i, registro in enumerate(registros, 1):
        data = {
            "username": USERNAME,
            "fecha": registro.get("fecha", ""),
            "obra": registro.get("obra", ""),
            "totalCantidad": registro.get("totalCantidad", 0),
            "totalCobrar": registro.get("totalCobrar", 0),
            "totalPagado": registro.get("totalPagado", 0),
            "status": registro.get("status", "pendiente"),
            "clientesAdicionales": registro.get("clientesAdicionales", ""),
            "detalles": registro.get("detalles", "")
        }
        if post_with_retry("/api/registros", data):
            success += 1
            if i % 10 == 0:
                print(f"  ✓ [{i}/{len(registros)}] Procesados...")
        time.sleep(0.2)
    
    print(f"  📊 Total: {success}/{len(registros)} registros migrados")
    return success == len(registros)

def main():
    print("=" * 70)
    print("🚀 MIGRACIÓN COMPLETA: LOCAL → RENDER")
    print("=" * 70)
    print(f"Usuario: {USERNAME}\n")
    
    if not wake_server():
        return
    
    # Obtener datos
    print("📂 Extrayendo datos locales...")
    data = get_local_data()
    
    if not data:
        print(f"✗ Usuario '{USERNAME}' no encontrado")
        return
    
    print(f"  ✓ {len(data['obras'])} obras")
    print(f"  ✓ {len(data['clientes'])} clientes")
    print(f"  ✓ {len(data['productos'])} productos")
    print(f"  ✓ {len(data['registros'])} registros")
    
    # Migrar en orden
    all_ok = True
    all_ok = migrate_obras(data["obras"]) and all_ok
    all_ok = migrate_clientes(data["clientes"]) and all_ok
    all_ok = migrate_productos(data["productos"]) and all_ok
    all_ok = migrate_registros(data["registros"]) and all_ok
    
    print("\n" + "=" * 70)
    if all_ok:
        print("✅ MIGRACIÓN COMPLETADA CON ÉXITO")
    else:
        print("⚠️  MIGRACIÓN COMPLETADA CON ALGUNOS ERRORES")
    print("=" * 70)
    print(f"\nAccede a: https://aplicaci-n-mi.vercel.app")
    print(f"Usuario: {USERNAME}")
    print(f"Contraseña: Panchita123")
    print()

if __name__ == "__main__":
    main()
