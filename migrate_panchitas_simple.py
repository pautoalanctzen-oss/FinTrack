"""
Script simplificado para migrar datos de Panchita's Catering
1. Registra el usuario en producción
2. Migra todos los datos
"""
import sqlite3
import requests
import json
import time

LOCAL_DB = "backend/users.db"
RENDER_API = "https://aplicaci-n-mi.onrender.com"
USERNAME = "Panchita's Catering"
PASSWORD = "Panchitas2026"  # Contraseña para producción

print("=" * 70)
print(f"MIGRACIÓN: {USERNAME} → RENDER")
print("=" * 70)
print()

# 1. Obtener datos del usuario local
conn = sqlite3.connect(LOCAL_DB)
conn.row_factory = sqlite3.Row
user = conn.execute("SELECT * FROM users WHERE username = ?", (USERNAME,)).fetchone()

if not user:
    print(f"❌ Usuario '{USERNAME}' no encontrado en BD local")
    exit(1)

print(f"✓ Usuario encontrado en BD local")
print(f"  Email: {user['email']}")
print(f"  Birthdate: {user['birthdate']}")
print()

# 2. Registrar usuario en producción
print("Registrando usuario en producción...")
try:
    response = requests.post(
        f"{RENDER_API}/api/register",
        data={
            "email": user['email'],
            "username": USERNAME,
            "birthdate": user['birthdate'],
            "password": PASSWORD,
            "confirm_password": PASSWORD
        },
        timeout=15
    )
    
    if response.status_code == 200:
        print(f"✓ Usuario registrado exitosamente")
        print(f"  📝 Contraseña: {PASSWORD}")
    elif "ya existe" in response.text.lower() or "already" in response.text.lower():
        print(f"✓ Usuario ya existe en producción")
    else:
        print(f"❌ Error al registrar: {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

print()

# 3. Obtener datos a migrar
print("Extrayendo datos locales...")
user_id = user['id']

obras = conn.execute("SELECT * FROM obras WHERE user_id = ?", (user_id,)).fetchall()
clientes = conn.execute("SELECT * FROM clientes WHERE user_id = ?", (user_id,)).fetchall()
productos = conn.execute("SELECT * FROM productos WHERE user_id = ?", (user_id,)).fetchall()
registros = conn.execute("SELECT * FROM registros WHERE user_id = ?", (user_id,)).fetchall()

print(f"  - {len(productos)} productos")
print(f"  - {len(obras)} obras")
print(f"  - {len(clientes)} clientes")
print(f"  - {len(registros)} registros")
print()

conn.close()

# 4. Migrar PRODUCTOS primero
print(f"Migrando {len(productos)} productos...")
migrados_productos = 0
for p in productos:
    try:
        r = requests.post(f"{RENDER_API}/api/productos",
            data={"username": USERNAME, "nombre": p["nombre"], "precio": p["precio"]},
            timeout=10)
        if r.status_code == 200:
            migrados_productos += 1
            print(f"  ✓ {p['nombre']}")
        else:
            print(f"  ✗ {p['nombre']}: {r.text[:80]}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    time.sleep(0.2)
print(f"  Total: {migrados_productos}/{len(productos)}")
print()

# 5. Migrar OBRAS
print(f"Migrando {len(obras)} obras...")
migrados_obras = 0
for o in obras:
    try:
        r = requests.post(f"{RENDER_API}/api/obras",
            data={"username": USERNAME, "nombre": o["nombre"], 
                  "ubicacion": o["ubicacion"] or "", "estado": o["estado"] or "activa"},
            timeout=10)
        if r.status_code == 200:
            migrados_obras += 1
            if migrados_obras % 5 == 0:
                print(f"  ... {migrados_obras} obras migradas")
        else:
            print(f"  ✗ {o['nombre']}: {r.text[:80]}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    time.sleep(0.2)
print(f"  Total: {migrados_obras}/{len(obras)}")
print()

# 6. Migrar CLIENTES
print(f"Migrando {len(clientes)} clientes...")
migrados_clientes = 0
for c in clientes:
    try:
        r = requests.post(f"{RENDER_API}/api/clientes",
            data={"username": USERNAME, "nombre": c["nombre"], "cedula": c["cedula"] or "",
                  "obra": c["obra"] or "", "estado": c["estado"] or "activo", 
                  "fecha": c["fecha"] or ""},
            timeout=10)
        if r.status_code == 200:
            migrados_clientes += 1
            if migrados_clientes % 10 == 0:
                print(f"  ... {migrados_clientes} clientes migrados")
        else:
            print(f"  ✗ {c['nombre']}: {r.text[:80]}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    time.sleep(0.2)
print(f"  Total: {migrados_clientes}/{len(clientes)}")
print()

# 7. Migrar REGISTROS
print(f"Migrando {len(registros)} registros...")
migrados_registros = 0
for reg in registros:
    try:
        # Preparar JSON
        payload = {
            "username": USERNAME,
            "fecha": reg["fecha"],
            "obra": reg["obra"],
            "totalCantidad": reg["totalCantidad"] or 0,
            "totalCobrar": float(reg["totalCobrar"] or 0),
            "totalPagado": float(reg["totalPagado"] or 0),
            "status": reg["status"] or "pendiente",
            "clientesAdicionales": json.loads(reg["clientesAdicionales"]) if reg["clientesAdicionales"] else [],
            "detalles": json.loads(reg["detalles"]) if reg["detalles"] else []
        }
        
        r = requests.post(f"{RENDER_API}/api/registros",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10)
        
        if r.status_code == 200:
            migrados_registros += 1
            if migrados_registros % 20 == 0:
                print(f"  ... {migrados_registros} registros migrados")
        else:
            print(f"  ✗ Registro {reg['id']}: {r.text[:80]}")
    except Exception as e:
        print(f"  ✗ Error registro {reg['id']}: {e}")
    time.sleep(0.2)
print(f"  Total: {migrados_registros}/{len(registros)}")
print()

# RESUMEN
print("=" * 70)
print("RESUMEN DE MIGRACIÓN")
print("=" * 70)
print(f"✓ Productos: {migrados_productos}/{len(productos)}")
print(f"✓ Obras: {migrados_obras}/{len(obras)}")
print(f"✓ Clientes: {migrados_clientes}/{len(clientes)}")
print(f"✓ Registros: {migrados_registros}/{len(registros)}")
print()

total = migrados_productos + migrados_obras + migrados_clientes + migrados_registros
esperado = len(productos) + len(obras) + len(clientes) + len(registros)

if total == esperado:
    print("🎉 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
else:
    print(f"⚠️  Migración parcial: {total}/{esperado}")

print()
print("Accede a: https://aplicaci-n-mi.vercel.app")
print(f"Usuario: {USERNAME}")
print(f"Contraseña: {PASSWORD}")
print()
