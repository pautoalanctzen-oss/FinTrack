"""
Script robusto para migrar datos de Panchita's Catering a Render
Verifica que el usuario exista antes de migrar
"""
import sqlite3
import requests
import json
from datetime import datetime
import time

# Configuración
LOCAL_DB = "backend/users.db"
RENDER_API = "https://aplicaci-n-mi.onrender.com"
USERNAME = "Panchita's Catering"

def check_user_exists():
    """Verifica si el usuario existe en producción"""
    try:
        response = requests.get(f"{RENDER_API}/api/user?username={USERNAME}", timeout=10)
        if response.status_code == 200:
            print(f"✓ Usuario '{USERNAME}' existe en producción")
            return True
        else:
            print(f"✗ Usuario '{USERNAME}' NO existe en producción (código {response.status_code})")
            print(f"  Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error verificando usuario: {e}")
        return False

def get_user_id_local(username):
    """Obtiene el user_id del usuario en la DB local"""
    conn = sqlite3.connect(LOCAL_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT id, email, password_hash, birthdate FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def register_user_in_production(user_data):
    """Registra el usuario en producción si no existe"""
    print(f"\nIntentando registrar usuario en producción...")
    print(f"  Email: {user_data['email']}")
    print(f"  Username: {USERNAME}")
    print(f"  Birthdate: {user_data['birthdate']}")
    
    # Nota: No podemos usar el hash existente, necesitamos crear una contraseña nueva
    # El usuario deberá usar esta contraseña para login
    password = "Panchitas2026"  # Contraseña temporal
    
    try:
        response = requests.post(
            f"{RENDER_API}/api/register",
            data={
                "email": user_data['email'],
                "username": USERNAME,
                "birthdate": user_data['birthdate'],
                "password": password,
                "confirm_password": password
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✓ Usuario registrado exitosamente")
            print(f"  IMPORTANTE: Contraseña temporal: {password}")
            return True
        else:
            print(f"✗ Error al registrar: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

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
                },
                timeout=10
            )
            if response.status_code == 200:
                success += 1
                print(f"  ✓ Obra '{obra['nombre']}'")
            else:
                print(f"  ✗ Error en obra '{obra['nombre']}': {response.text[:100]}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
        time.sleep(0.1)  # Pequeña pausa para no sobrecargar
    print(f"  Total: {success}/{len(obras)} obras migradas")
    return success

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
                },
                timeout=10
            )
            if response.status_code == 200:
                success += 1
                if success % 10 == 0:
                    print(f"  ... {success} clientes migrados")
            else:
                print(f"  ✗ Error en cliente '{cliente['nombre']}': {response.text[:100]}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
        time.sleep(0.1)
    print(f"  Total: {success}/{len(clientes)} clientes migrados")
    return success

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
                },
                timeout=10
            )
            if response.status_code == 200:
                success += 1
                print(f"  ✓ Producto '{producto['nombre']}'")
            else:
                print(f"  ✗ Error en producto '{producto['nombre']}': {response.text[:100]}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
        time.sleep(0.1)
    print(f"  Total: {success}/{len(productos)} productos migrados")
    return success

def migrate_registros(registros):
    """Migra registros a Render"""
    print(f"\nMigrando {len(registros)} registros...")
    success = 0
    for i, registro in enumerate(registros, 1):
        try:
            # Preparar payload JSON
            payload = {
                "username": USERNAME,
                "fecha": registro.get("fecha"),
                "obra": registro.get("obra"),
                "totalCantidad": registro.get("totalCantidad", 0),
                "totalCobrar": float(registro.get("totalCobrar", 0)),
                "totalPagado": float(registro.get("totalPagado", 0)),
                "status": registro.get("status", "pendiente"),
                "clientesAdicionales": json.loads(registro.get("clientesAdicionales", "[]")) if registro.get("clientesAdicionales") else [],
                "detalles": json.loads(registro.get("detalles", "[]")) if registro.get("detalles") else []
            }
            
            response = requests.post(
                f"{RENDER_API}/api/registros",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                success += 1
                if success % 20 == 0:
                    print(f"  ... {success} registros migrados")
            else:
                print(f"  ✗ Error en registro {i}: {response.text[:100]}")
        except Exception as e:
            print(f"  ✗ Error en registro {i}: {e}")
        time.sleep(0.1)
    print(f"  Total: {success}/{len(registros)} registros migrados")
    return success

def main():
    print("=" * 70)
    print(f"MIGRACIÓN ROBUSTA DE DATOS: {USERNAME} → RENDER")
    print("=" * 70)
    print()
    
    # 1. Verificar que Render esté activo
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
    
    # 2. Obtener datos del usuario local
    user_data = get_user_id_local(USERNAME)
    if not user_data:
        print(f"✗ Usuario '{USERNAME}' no encontrado en la base de datos local")
        return
    
    print(f"✓ Usuario encontrado en DB local (ID: {user_data['id']})")
    print()
    
    # 3. Verificar si el usuario existe en producción
    if not check_user_exists():
        print("\n¿Desea registrar el usuario en producción? (s/n): ", end="")
        response = input().strip().lower()
        if response == 's':
            if not register_user_in_production(user_data):
                print("\n✗ No se pudo registrar el usuario. Abortando migración.")
                return
        else:
            print("\n✗ Migración cancelada.")
            return
    
    print()
    
    # 4. Obtener datos locales
    print("Extrayendo datos de la base de datos local...")
    data = get_local_data(user_data['id'])
    
    print(f"  - {len(data['obras'])} obras")
    print(f"  - {len(data['clientes'])} clientes")
    print(f"  - {len(data['productos'])} productos")
    print(f"  - {len(data['registros'])} registros")
    print()
    
    # 5. Confirmar migración
    print("¿Continuar con la migración? (s/n): ", end="")
    confirm = input().strip().lower()
    if confirm != 's':
        print("\n✗ Migración cancelada.")
        return
    
    print()
    
    # 6. Migrar cada tipo de dato
    results = {
        "obras": migrate_obras(data["obras"]),
        "clientes": migrate_clientes(data["clientes"]),
        "productos": migrate_productos(data["productos"]),
        "registros": migrate_registros(data["registros"])
    }
    
    # 7. Resumen
    print()
    print("=" * 70)
    print("RESUMEN DE MIGRACIÓN")
    print("=" * 70)
    print(f"✓ Obras migradas: {results['obras']}/{len(data['obras'])}")
    print(f"✓ Clientes migrados: {results['clientes']}/{len(data['clientes'])}")
    print(f"✓ Productos migrados: {results['productos']}/{len(data['productos'])}")
    print(f"✓ Registros migrados: {results['registros']}/{len(data['registros'])}")
    print()
    
    total_migrado = sum(results.values())
    total_esperado = sum(len(data[k]) for k in data.keys())
    
    if total_migrado == total_esperado:
        print("🎉 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
    else:
        print(f"⚠️  Migración parcial: {total_migrado}/{total_esperado} registros")
    
    print()
    print("Puedes verificar los datos en:")
    print(f"  https://aplicaci-n-mi.vercel.app")
    print(f"  Usuario: {USERNAME}")
    print()

if __name__ == "__main__":
    main()
