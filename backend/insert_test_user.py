#!/usr/bin/env python3
"""
Script para crear un usuario de prueba en Neon.
Usuario: panchita
Contraseña: Panchita123!
"""
import os
import sys
import psycopg2
import bcrypt

# Obtener DATABASE_URL
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL no está definido")
    sys.exit(1)

try:
    conn = psycopg2.connect(DATABASE_URL, sslmode='require', channel_binding='require')
    cursor = conn.cursor()
    print("✅ Conectado a Neon")
    
    # Datos del usuario
    email = "panchita@catering.com"
    username = "panchita"
    password = "Panchita123!"
    birthdate = "1990-01-15"
    
    # Hash de la contraseña
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    print(f"\n👤 Insertando usuario:")
    print(f"   Email: {email}")
    print(f"   Username: {username}")
    print(f"   Birthdate: {birthdate}")
    print(f"   Hash: {password_hash[:30]}...")
    
    # Insertar usuario
    cursor.execute("""
        INSERT INTO users (email, username, birthdate, password_hash)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (username) DO UPDATE 
        SET password_hash = EXCLUDED.password_hash
    """, (email, username, birthdate, password_hash))
    
    conn.commit()
    print("\n✅✅✅ Usuario 'panchita' creado/actualizado CORRECTAMENTE ✅✅✅")
    print(f"\n📝 Credenciales de prueba:")
    print(f"   Usuario: {username}")
    print(f"   Contraseña: {password}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
