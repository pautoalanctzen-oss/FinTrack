"""
Migración SOLO de registros de Panchita's Catering
"""
import sqlite3
import requests
import json
import time

LOCAL_DB = "backend/users.db"
RENDER_API = "https://aplicaci-n-mi.onrender.com"
USERNAME = "Panchita's Catering"

print("=" * 70)
print("MIGRACIÓN DE REGISTROS ÚNICAMENTE")
print("=" * 70)
print()

# Obtener registros locales
conn = sqlite3.connect(LOCAL_DB)
conn.row_factory = sqlite3.Row

user = conn.execute("SELECT id FROM users WHERE username = ?", (USERNAME,)).fetchone()
user_id = user['id']

registros = [dict(r) for r in conn.execute(
    "SELECT * FROM registros WHERE user_id = ? ORDER BY fecha", 
    (user_id,)
).fetchall()]

conn.close()

print(f"Total de registros a migrar: {len(registros)}")
print()

# Migrar registros
migrados = 0
errores = 0

for i, reg in enumerate(registros, 1):
    try:
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
            timeout=30
        )
        
        if r.status_code == 200:
            migrados += 1
            if migrados % 10 == 0:
                print(f"  [{migrados}/{len(registros)}] {(migrados/len(registros)*100):.1f}%")
        else:
            errores += 1
            if errores <= 3:
                print(f"  ✗ Error en {reg['fecha']}: {r.text[:100]}")
                
    except Exception as e:
        errores += 1
        if errores <= 3:
            print(f"  ✗ Error: {str(e)[:100]}")
    
    time.sleep(0.2)  # Pausa para no sobrecargar Render

print()
print(f"✓ Migrados: {migrados}/{len(registros)}")
print(f"✗ Errores: {errores}")
print()

if migrados == len(registros):
    print("¡MIGRACIÓN COMPLETADA!")
else:
    print(f"Migración parcial: {(migrados/len(registros)*100):.1f}%")
