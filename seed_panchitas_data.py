"""
Script para generar datos de ejemplo para Panchita's Catering
"""
import sqlite3
from datetime import datetime, timedelta
import random

conn = sqlite3.connect('backend/users.db')
cursor = conn.cursor()

# Obtener ID del usuario Panchita's Catering
cursor.execute("SELECT id FROM users WHERE username = ?", ("Panchita's Catering",))
result = cursor.fetchone()
if not result:
    print("Error: No se encontró el usuario 'Panchita's Catering'")
    conn.close()
    exit(1)

user_id = result[0]
print(f"Usuario 'Panchita's Catering' encontrado con ID: {user_id}")

# 1. Crear 2 productos
print("\nCreando productos...")
productos = [
    ("Almuerzo Completo", 35.00),
    ("Refrigerio", 15.00)
]

for nombre, precio in productos:
    cursor.execute("""
        INSERT INTO productos (user_id, nombre, precio, created_at)
        VALUES (?, ?, ?, ?)
    """, (user_id, nombre, precio, datetime.now().isoformat()))
print(f"✓ {len(productos)} productos creados")

# 2. Crear 10 obras
print("\nCreando obras...")
obras_nombres = [
    "Construcción Edificio Central",
    "Remodelación Hospital Regional",
    "Proyecto Residencial Los Pinos",
    "Centro Comercial Plaza Norte",
    "Complejo Deportivo Municipal",
    "Escuela Primaria Nueva Esperanza",
    "Parque Industrial Este",
    "Urbanización Vista Hermosa",
    "Oficinas Corporativas Torre Sur",
    "Conjunto Habitacional El Bosque"
]

ubicaciones = [
    "Av. Principal 123",
    "Calle Real 456",
    "Zona Norte",
    "Sector Industrial",
    "Barrio Centro",
    "Urbanización El Parque",
    "Zona Este",
    "Sector Residencial",
    "Av. Comercial 789",
    "Calle Nueva 321"
]

obras_ids = []
for i, nombre in enumerate(obras_nombres):
    cursor.execute("""
        INSERT INTO obras (user_id, nombre, ubicacion, estado, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, nombre, ubicaciones[i], "activa", datetime.now().isoformat()))
    obras_ids.append(cursor.lastrowid)
print(f"✓ {len(obras_ids)} obras creadas")

# 3. Crear ~50 clientes (5 por obra)
print("\nCreando clientes...")
nombres = [
    "Juan Pérez", "María García", "Carlos López", "Ana Martínez", "Luis Rodríguez",
    "Carmen Sánchez", "José González", "Laura Fernández", "Miguel Torres", "Isabel Ramírez",
    "Francisco Díaz", "Patricia Moreno", "Antonio Jiménez", "Rosa Álvarez", "Manuel Romero",
    "Lucía Navarro", "Pedro Ruiz", "Teresa Iglesias", "Ramón Castro", "Pilar Ortiz",
    "Alberto Delgado", "Sofía Marín", "Javier Rubio", "Elena Gil", "Fernando Serrano",
    "Cristina Molina", "Diego Blanco", "Beatriz Suárez", "Sergio Ortega", "Marta Vega",
    "Ricardo Morales", "Alicia Medina", "Ángel Cabrera", "Raquel Guerrero", "Pablo Prieto",
    "Silvia Flores", "Víctor Cano", "Mónica Peña", "Andrés León", "Natalia Márquez",
    "David Herrera", "Julia Sanz", "Oscar Domínguez", "Irene Vázquez", "Rubén Giménez",
    "Eva Santos", "Guillermo Hidalgo", "Nuria Pascual", "Adrián Lozano", "Cristina Parra"
]

clientes_ids_por_obra = {}
cliente_idx = 0

for obra_id, obra_nombre in zip(obras_ids, obras_nombres):
    clientes_ids_por_obra[obra_id] = []
    for i in range(5):  # 5 clientes por obra = 50 total
        nombre = nombres[cliente_idx % len(nombres)]
        cedula = f"{1000000 + cliente_idx:07d}"
        estado = "activo"
        fecha = (datetime.now() - timedelta(days=random.randint(30, 180))).date().isoformat()
        
        cursor.execute("""
            INSERT INTO clientes (user_id, nombre, cedula, obra, estado, fecha, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, nombre, cedula, obra_nombre, estado, fecha, datetime.now().isoformat()))
        
        clientes_ids_por_obra[obra_id].append(cursor.lastrowid)
        cliente_idx += 1

print(f"✓ {cliente_idx} clientes creados")

# 4. Crear registros (15 por obra = 150 total)
print("\nCreando registros...")
total_registros = 0

for obra_id, obra_nombre in zip(obras_ids, obras_nombres):
    for reg_num in range(15):  # 15 registros por obra
        # Fecha aleatoria en los últimos 90 días
        fecha = (datetime.now() - timedelta(days=random.randint(1, 90))).date().isoformat()
        
        # Generar detalles aleatorios (mezcla de productos)
        num_productos = random.randint(3, 8)
        detalles = []
        total_cantidad = 0
        total_cobrar = 0
        
        for _ in range(num_productos):
            producto_idx = random.randint(0, 1)  # 0: Almuerzo, 1: Refrigerio
            producto_nombre = productos[producto_idx][0]
            precio = productos[producto_idx][1]
            cantidad = random.randint(5, 25)
            
            detalles.append({
                "producto": producto_nombre,
                "cantidad": cantidad,
                "precio": precio,
                "cliente": random.choice(nombres)
            })
            
            total_cantidad += cantidad
            total_cobrar += cantidad * precio
        
        # Status aleatorio: 70% pagado, 20% parcial, 10% pendiente
        rand = random.random()
        if rand < 0.7:
            status = "pagado"
            total_pagado = total_cobrar
        elif rand < 0.9:
            status = "parcial"
            total_pagado = total_cobrar * random.uniform(0.3, 0.8)
        else:
            status = "pendiente"
            total_pagado = 0
        
        # Clientes adicionales vacío para registros de obra
        import json
        detalles_json = json.dumps(detalles)
        
        cursor.execute("""
            INSERT INTO registros (
                user_id, fecha, obra, totalCantidad, totalCobrar, totalPagado, 
                status, clientesAdicionales, detalles, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, fecha, obra_nombre, total_cantidad, total_cobrar, total_pagado,
            status, "[]", detalles_json, datetime.now().isoformat()
        ))
        
        total_registros += 1

print(f"✓ {total_registros} registros creados")

# Confirmar cambios
conn.commit()

# Mostrar resumen final
print("\n" + "="*50)
print("RESUMEN DE DATOS GENERADOS")
print("="*50)

cursor.execute("SELECT COUNT(*) FROM productos WHERE user_id = ?", (user_id,))
print(f"Productos: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM obras WHERE user_id = ?", (user_id,))
print(f"Obras: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM clientes WHERE user_id = ?", (user_id,))
print(f"Clientes: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM registros WHERE user_id = ?", (user_id,))
print(f"Registros: {cursor.fetchone()[0]}")

print("\n✅ Datos de ejemplo generados exitosamente para Panchita's Catering")

conn.close()
