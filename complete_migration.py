"""
Script final para completar la migración de Panchita's Catering
Migra solo lo que falta: clientes y registros
"""
import sqlite3
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

LOCAL_DB = "backend/users.db"
RENDER_API = "https://aplicaci-n-mi.onrender.com"
USERNAME = "Panchita's Catering"

print("=" * 70)
print("COMPLETANDO MIGRACIÓN: Clientes y Registros")
print("=" * 70)
print()

# Obtener datos
conn = sqlite3.connect(LOCAL_DB)
conn.row_factory = sqlite3.Row

user = conn.execute("SELECT id FROM users WHERE username = ?", (USERNAME,)).fetchone()
user_id = user['id']

clientes = [dict(c) for c in conn.execute("SELECT * FROM clientes WHERE user_id = ?", (user_id,)).fetchall()]
registros = [dict(reg) for reg in conn.execute("SELECT * FROM registros WHERE user_id = ?", (user_id,)).fetchall()]

conn.close()

print(f"A migrar:")
print(f"  - {len(clientes)} clientes")
print(f"  - {len(registros)} registros")
print()

# Migrar CLIENTES (uno por uno para ver progreso)
print(f"Migrando {len(clientes)} clientes...")
migrados_clientes = 0
errores_clientes = 0

for i, c in enumerate(clientes, 1):
    try:
        r = requests.post(
            f"{RENDER_API}/api/clientes",
            data={
                "username": USERNAME,
                "nombre": c["nombre"],
                "cedula": c["cedula"] or "",
                "obra": c["obra"] or "",
                "estado": c["estado"] or "activo",
                "fecha": c["fecha"] or ""
            },
            timeout=15
        )
        
        if r.status_code == 200:
            migrados_clientes += 1
            if migrados_clientes % 5 == 0:
                print(f"  ... {migrados_clientes}/{len(clientes)}")
        else:
            errores_clientes += 1
            if errores_clientes <= 3:
                print(f"  X Error en '{c['nombre']}': {r.text[:60]}")
                
    except Exception as e:
        errores_clientes += 1
        if errores_clientes <= 3:
            print(f"  X Error: {str(e)[:60]}")
    
    time.sleep(0.15)  # Pausa entre peticiones

print(f"  Total clientes: {migrados_clientes}/{len(clientes)}")
print()

# Migrar REGISTROS
print(f"Migrando {len(registros)} registros...")
migrados_registros = 0
errores_registros = 0

for i, reg in enumerate(registros, 1):
    try:
        # Preparar payload JSON
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
        
        r = requests.post(
            f"{RENDER_API}/api/registros",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if r.status_code == 200:
            migrados_registros += 1
            if migrados_registros % 10 == 0:
                print(f"  ... {migrados_registros}/{len(registros)}")
        else:
            errores_registros += 1
            if errores_registros <= 3:
                print(f"  X Error en registro {reg['id']}: {r.text[:60]}")
                
    except Exception as e:
        errores_registros += 1
        if errores_registros <= 3:
            print(f"  X Error: {str(e)[:60]}")
    
    time.sleep(0.15)

print(f"  Total registros: {migrados_registros}/{len(registros)}")
print()

# RESUMEN
print("=" * 70)
print("RESUMEN FINAL")
print("=" * 70)
print(f"✓ Clientes migrados: {migrados_clientes}/{len(clientes)}")
print(f"✓ Registros migrados: {migrados_registros}/{len(registros)}")

if errores_clientes > 0:
    print(f"  - Errores en clientes: {errores_clientes}")
if errores_registros > 0:
    print(f"  - Errores en registros: {errores_registros}")

print()

total = migrados_clientes + migrados_registros
esperado = len(clientes) + len(registros)

if total == esperado:
    print("¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
else:
    print(f"Migración parcial: {total}/{esperado}")

print()
print("Usuario: Panchita's Catering")
print("Contraseña: Panchitas2026")
print("URL: https://aplicaci-n-mi.vercel.app")
print()
