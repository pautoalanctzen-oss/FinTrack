"""
Migración de 145 registros de Panchita's Catering a Render
Optimizado para mostrar progreso y manejar errores
"""
import sqlite3
import requests
import json
import time
from datetime import datetime

LOCAL_DB = "backend/users.db"
RENDER_API = "https://aplicaci-n-mi.onrender.com"
USERNAME = "Panchita's Catering"

print("=" * 70)
print("MIGRACIÓN DE REGISTROS - Panchita's Catering")
print("=" * 70)
print(f"Inicio: {datetime.now().strftime('%H:%M:%S')}")
print()

# Obtener registros de la BD local
conn = sqlite3.connect(LOCAL_DB)
conn.row_factory = sqlite3.Row
user = conn.execute("SELECT id FROM users WHERE username = ?", (USERNAME,)).fetchone()
user_id = user['id']

registros = [dict(reg) for reg in conn.execute(
    "SELECT * FROM registros WHERE user_id = ? ORDER BY fecha", 
    (user_id,)
).fetchall()]

conn.close()

print(f"Total de registros a migrar: {len(registros)}")
print()

# Migrar registros
migrados = 0
errores = 0
errores_detalle = []

for i, reg in enumerate(registros, 1):
    try:
        # Preparar payload
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
        
        # Enviar con timeout generoso
        r = requests.post(
            f"{RENDER_API}/api/registros",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30  # 30 segundos de timeout
        )
        
        if r.status_code == 200:
            migrados += 1
            # Mostrar progreso cada 5 registros
            if migrados % 5 == 0:
                porcentaje = (migrados / len(registros)) * 100
                print(f"  [{migrados}/{len(registros)}] {porcentaje:.1f}% - {reg['fecha']} | {reg['obra']}")
        else:
            errores += 1
            error_msg = f"Registro {i} ({reg['fecha']}): {r.status_code} - {r.text[:80]}"
            errores_detalle.append(error_msg)
            if errores <= 5:  # Mostrar solo los primeros 5 errores
                print(f"  ✗ {error_msg}")
                
    except requests.exceptions.Timeout:
        errores += 1
        error_msg = f"Registro {i} ({reg['fecha']}): TIMEOUT"
        errores_detalle.append(error_msg)
        if errores <= 5:
            print(f"  ✗ {error_msg}")
    except Exception as e:
        errores += 1
        error_msg = f"Registro {i} ({reg['fecha']}): {str(e)[:80]}"
        errores_detalle.append(error_msg)
        if errores <= 5:
            print(f"  ✗ {error_msg}")
    
    # Pausa pequeña entre peticiones para no sobrecargar Render
    time.sleep(0.3)
    
    # Cada 20 registros, hacer una pausa más larga
    if i % 20 == 0:
        print(f"  ... Pausa breve (ya van {migrados} migrados)")
        time.sleep(2)

# Resumen final
print()
print("=" * 70)
print("RESUMEN DE MIGRACIÓN")
print("=" * 70)
print(f"Fin: {datetime.now().strftime('%H:%M:%S')}")
print(f"Registros migrados: {migrados}/{len(registros)}")
print(f"Errores: {errores}")

if migrados == len(registros):
    print()
    print("¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
elif migrados > 0:
    porcentaje = (migrados / len(registros)) * 100
    print()
    print(f"Migración parcial: {porcentaje:.1f}% completado")
    print(f"Faltan {len(registros) - migrados} registros por migrar")
else:
    print()
    print("No se pudo migrar ningún registro. Revisar conexión a Render.")

# Mostrar resumen de errores si hay muchos
if errores > 5:
    print()
    print(f"Se ocultaron {errores - 5} errores adicionales.")
    print("Los primeros 5 errores están listados arriba.")

print()
print("Para verificar los datos migrados:")
print(f"https://aplicaci-n-mi.onrender.com/api/registros?username={USERNAME}")
print()
