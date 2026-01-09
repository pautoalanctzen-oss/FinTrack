"""
Script para migrar SOLO productos y registros (lo que faltó)
"""
import sqlite3
import requests
import time
import json

LOCAL_DB = "backend/users.db"
RENDER_API = "https://aplicaci-n-mi.onrender.com"
USERNAME = "Panchita's Catering"

def get_data():
    """Obtiene productos y registros pendientes"""
    conn = sqlite3.connect(LOCAL_DB)
    conn.row_factory = sqlite3.Row
    
    user = conn.execute("SELECT id FROM users WHERE username = ?", (USERNAME,)).fetchone()
    if not user:
        conn.close()
        return None
    
    user_id = user["id"]
    
    productos = [dict(row) for row in conn.execute("SELECT * FROM productos WHERE user_id = ?", (user_id,))]
    registros = [dict(row) for row in conn.execute("SELECT * FROM registros WHERE user_id = ? ORDER BY id", (user_id,))]
    
    conn.close()
    return {"productos": productos, "registros": registros}

def migrate_productos(productos):
    """Migra productos"""
    print(f"\n📦 Migrando {len(productos)} productos...")
    success = 0
    
    for i, producto in enumerate(productos, 1):
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
                print(f"  ✓ {producto['nombre']}")
            time.sleep(0.5)
        except Exception as e:
            print(f"  ✗ {producto['nombre']}: {str(e)[:50]}")
    
    print(f"  Total: {success}/{len(productos)} ✓")
    return success

def migrate_registros_batch(registros):
    """Migra registros en lotes más eficientes"""
    print(f"\n📝 Migrando {len(registros)} registros...")
    success = 0
    failed = 0
    batch_size = 10
    
    for batch_start in range(0, len(registros), batch_size):
        batch_end = min(batch_start + batch_size, len(registros))
        batch = registros[batch_start:batch_end]
        
        for i, registro in enumerate(batch, 1):
            actual_index = batch_start + i
            try:
                data = {
                    "username": USERNAME,
                    "fecha": registro.get("fecha", ""),
                    "obra": registro.get("obra", ""),
                    "totalCantidad": int(registro.get("totalCantidad", 0)),
                    "totalCobrar": float(registro.get("totalCobrar", 0)),
                    "totalPagado": float(registro.get("totalPagado", 0)),
                    "status": registro.get("status", "pendiente"),
                    "clientesAdicionales": registro.get("clientesAdicionales", ""),
                    "detalles": registro.get("detalles", "")
                }
                
                response = requests.post(
                    f"{RENDER_API}/api/registros",
                    data=data,
                    timeout=15
                )
                
                if response.status_code == 200:
                    success += 1
                    if actual_index % 20 == 0:
                        print(f"  ✓ [{actual_index}/{len(registros)}]")
                else:
                    failed += 1
                
                time.sleep(0.1)  # Delay pequeño para no saturar
            except Exception as e:
                failed += 1
                if actual_index % 25 == 0:
                    print(f"  ⚠ [{actual_index}/{len(registros)}]")
    
    print(f"  Total: {success}/{len(registros)} ✓ | {failed} errores")
    return success

def main():
    print("=" * 70)
    print("🚀 MIGRACIÓN FINAL: Productos + Registros")
    print("=" * 70)
    
    # Obtener datos
    print("\n📂 Cargando datos pendientes...")
    data = get_data()
    
    if not data:
        print("✗ No se encontraron datos")
        return
    
    print(f"  ✓ {len(data['productos'])} productos")
    print(f"  ✓ {len(data['registros'])} registros")
    
    # Migrar
    prod_success = migrate_productos(data["productos"])
    reg_success = migrate_registros_batch(data["registros"])
    
    print("\n" + "=" * 70)
    print("✅ MIGRACIÓN FINALIZADA")
    print("=" * 70)
    print(f"\n📊 Resultados:")
    print(f"   Productos: {prod_success}/{len(data['productos'])} ✓")
    print(f"   Registros: {reg_success}/{len(data['registros'])} ✓")
    print(f"\n🎯 Accede a: https://aplicaci-n-mi.vercel.app")
    print()

if __name__ == "__main__":
    main()
