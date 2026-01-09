import sqlite3
import json
from datetime import datetime

# Cargar el backup
print("Cargando backup_panchitas_exacto.json...")
with open(r'C:\Users\pauto\Downloads\backup_panchitas_exacto.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Datos cargados:")
print(f"  - Clientes: {len(data['clientes'])}")
print(f"  - Obras: {len(data['obras'])}")
print(f"  - Productos: {len(data['productos'])}")
print(f"  - Registros: {len(data['registros'])}")

# Conectar a la base de datos
conn = sqlite3.connect('backend/users.db')
cursor = conn.cursor()

# Obtener ID del usuario Panchita's Catering
cursor.execute("SELECT id FROM users WHERE username = ?", ("Panchita's Catering",))
result = cursor.fetchone()
if not result:
    print("ERROR: Usuario 'Panchita's Catering' no encontrado")
    exit(1)

user_id = result[0]
print(f"\nUsuario encontrado con ID: {user_id}")

# LIMPIAR datos existentes del usuario
print("\nLimpiando datos existentes...")
cursor.execute("DELETE FROM registros WHERE user_id = ?", (user_id,))
cursor.execute("DELETE FROM clientes WHERE user_id = ?", (user_id,))
cursor.execute("DELETE FROM obras WHERE user_id = ?", (user_id,))
cursor.execute("DELETE FROM productos WHERE user_id = ?", (user_id,))
print("Datos antiguos eliminados")

# 1. MIGRAR PRODUCTOS
print("\nMigrando productos...")
for producto in data['productos']:
    cursor.execute("""
        INSERT INTO productos (user_id, nombre, precio, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        user_id,
        producto['nombre'],
        producto['precio'],
        datetime.now().isoformat()
    ))
print(f"OK - {len(data['productos'])} productos migrados")

# 2. MIGRAR OBRAS
print("\nMigrando obras...")
for obra in data['obras']:
    cursor.execute("""
        INSERT INTO obras (user_id, nombre, ubicacion, estado, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        obra['nombre'],
        obra.get('ubicacion', ''),
        obra.get('estado', 'activa'),
        datetime.now().isoformat()
    ))
print(f"OK - {len(data['obras'])} obras migradas")

# 3. MIGRAR CLIENTES
print("\nMigrando clientes...")
for cliente in data['clientes']:
    cursor.execute("""
        INSERT INTO clientes (user_id, nombre, cedula, obra, estado, fecha, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        cliente['nombre'],
        cliente['cedula'],
        cliente['obra'],
        cliente.get('estado', 'activo'),
        cliente.get('fecha', datetime.now().date().isoformat()),
        datetime.now().isoformat()
    ))
print(f"OK - {len(data['clientes'])} clientes migrados")

# 4. MIGRAR REGISTROS
print("\nMigrando registros...")
for registro in data['registros']:
    # Convertir detalles a JSON string
    detalles = registro.get('detalles', [])
    if isinstance(detalles, list):
        detalles_json = json.dumps(detalles)
    else:
        detalles_json = detalles
    
    # Convertir clientesAdicionales a JSON string
    clientes_adicionales = registro.get('clientesAdicionales', [])
    if isinstance(clientes_adicionales, list):
        clientes_json = json.dumps(clientes_adicionales)
    else:
        clientes_json = clientes_adicionales
    
    cursor.execute("""
        INSERT INTO registros (
            user_id, fecha, obra, totalCantidad, totalCobrar, totalPagado,
            status, clientesAdicionales, detalles, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        registro['fecha'],
        registro['obra'],
        registro.get('totalCantidad', 0),
        registro.get('totalCobrar', 0),
        registro.get('totalPagado', 0),
        registro.get('status', 'pendiente'),
        clientes_json,
        detalles_json,
        datetime.now().isoformat()
    ))
print(f"OK - {len(data['registros'])} registros migrados")

# Commit y cerrar
conn.commit()
print("\n" + "="*60)
print("MIGRACION COMPLETADA EXITOSAMENTE")
print("="*60)

# Verificar totales
cursor.execute("SELECT COUNT(*) FROM productos WHERE user_id = ?", (user_id,))
print(f"Productos en DB: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM obras WHERE user_id = ?", (user_id,))
print(f"Obras en DB: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM clientes WHERE user_id = ?", (user_id,))
print(f"Clientes en DB: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM registros WHERE user_id = ?", (user_id,))
print(f"Registros en DB: {cursor.fetchone()[0]}")

print("\nTus datos originales han sido restaurados completamente.")
print("Ahora puedes iniciar el servidor y ver todo en el dashboard.")

conn.close()
