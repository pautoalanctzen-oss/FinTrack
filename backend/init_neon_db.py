#!/usr/bin/env python3
"""
Script para inicializar las tablas en Neon PostgreSQL directamente.
Ejecutar: python init_neon_db.py
"""
import os
import sys
import psycopg2
from psycopg2 import sql

# Obtener DATABASE_URL del ambiente
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL no está definido en las variables de entorno")
    sys.exit(1)

print(f"🔗 Conectando a: {DATABASE_URL[:50]}...")

try:
    # Conectar a la BD
    conn = psycopg2.connect(DATABASE_URL, sslmode='require', channel_binding='require')
    cursor = conn.cursor()
    print("✅ Conectado a Neon PostgreSQL")
    
    # Crear tablas
    print("\n📋 Creando tablas...")
    
    # Users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            birthdate TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Tabla users creada")
    
    # Obras
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS obras (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            ubicacion TEXT,
            estado TEXT DEFAULT 'activa',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    print("✅ Tabla obras creada")
    
    # Clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            cedula TEXT,
            obra TEXT,
            estado TEXT DEFAULT 'activo',
            fecha TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    print("✅ Tabla clientes creada")
    
    # Productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    print("✅ Tabla productos creada")
    
    # Registros
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            fecha TEXT,
            obra TEXT,
            totalCantidad INTEGER DEFAULT 0,
            totalCobrar REAL DEFAULT 0,
            totalPagado REAL DEFAULT 0,
            status TEXT DEFAULT 'pendiente',
            clientesAdicionales TEXT,
            detalles TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    print("✅ Tabla registros creada")
    
    # Commit
    conn.commit()
    print("\n✅✅✅ Base de datos inicializada CORRECTAMENTE ✅✅✅")
    
    # Verificar que las tablas existan
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    print(f"\n📊 Tablas existentes ({len(tables)}):")
    for table in tables:
        print(f"   - {table[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
