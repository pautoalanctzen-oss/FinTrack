"""
Script para migrar datos del usuario 'demo' a otro usuario existente
"""
import sqlite3
from datetime import datetime

DB_PATH = "backend/users.db"

def migrate_demo_to_user():
    """Migra los datos de demo a un usuario existente"""
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    try:
        # 1. Verificar si el usuario demo existe
        cursor = conn.execute("SELECT id, username FROM users WHERE username = 'demo'")
        demo_user = cursor.fetchone()
        
        if not demo_user:
            print("Error: Usuario 'demo' no encontrado")
            return False
        
        demo_id = demo_user['id']
        print(f"Usuario 'demo' encontrado (ID: {demo_id})")
        
        # 2. Mostrar usuarios disponibles
        print("\nUsuarios disponibles en la base de datos:")
        print("=" * 70)
        cursor = conn.execute("SELECT id, username, email FROM users WHERE username != 'demo' ORDER BY id")
        users = cursor.fetchall()
        
        if not users:
            print("No hay otros usuarios registrados.")
            print("\nPor favor, registra primero el usuario 'Panchita's Catering' desde:")
            print("   http://127.0.0.1:8000/register.html")
            print("\nLuego ejecuta este script nuevamente.")
            return False
        
        for user in users:
            print(f"   ID: {user['id']} - Usuario: {user['username']} - Email: {user['email']}")
        
        # 3. Pedir al usuario que seleccione
        print("\n" + "=" * 70)
        target_username = input("Ingresa el nombre de usuario al que deseas migrar los datos: ").strip()
        
        # Verificar que el usuario existe
        cursor = conn.execute("SELECT id, username FROM users WHERE username = ?", (target_username,))
        target_user = cursor.fetchone()
        
        if not target_user:
            print(f"\nError: Usuario '{target_username}' no encontrado")
            return False
        
        target_id = target_user['id']
        print(f"\nUsuario destino: {target_username} (ID: {target_id})")
        
        # 4. Contar datos del usuario demo
        print(f"\nContando datos del usuario 'demo' (ID: {demo_id})...")
        print("=" * 70)
        
        tables = ['clientes', 'obras', 'productos', 'registros']
        counts = {}
        
        for table in tables:
            cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table} WHERE user_id = ?", (demo_id,))
            result = cursor.fetchone()
            counts[table] = result['count']
            print(f"   {table}: {counts[table]} registros")
        
        total = sum(counts.values())
        
        if total == 0:
            print("\nEl usuario 'demo' no tiene datos para migrar")
            return True
        
        # 5. Confirmar migración
        print(f"\nSe migraran {total} registros en total")
        print(f"   Desde: demo (ID: {demo_id})")
        print(f"   Hacia: {target_username} (ID: {target_id})")
        
        response = input("\nContinuar con la migracion? (s/n): ")
        
        if response.lower() != 's':
            print("Migracion cancelada")
            return False
        
        # 6. Migrar datos
        print("\nMigrando datos...")
        
        for table in tables:
            if counts[table] > 0:
                cursor = conn.execute(
                    f"UPDATE {table} SET user_id = ? WHERE user_id = ?",
                    (target_id, demo_id)
                )
                print(f"   {table}: {cursor.rowcount} registros migrados")
        
        conn.commit()
        
        # 7. Verificar migración
        print("\nVerificando migracion...")
        for table in tables:
            cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table} WHERE user_id = ?", (target_id,))
            result = cursor.fetchone()
            print(f"   {table}: {result['count']} registros en {target_username}")
        
        # 8. Preguntar si eliminar usuario demo
        print(f"\nDeseas eliminar el usuario 'demo' ahora que sus datos fueron migrados?")
        response = input("   (s/n): ")
        
        if response.lower() == 's':
            conn.execute("DELETE FROM users WHERE id = ?", (demo_id,))
            conn.commit()
            print("   Usuario 'demo' eliminado")
        else:
            print("   Usuario 'demo' conservado (sin datos)")
        
        print("\n" + "=" * 70)
        print("MIGRACION COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print(f"\nPuedes iniciar sesion con:")
        print(f"   Usuario: {target_username}")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 70)
    print("MIGRACION DE DATOS: demo -> Otro usuario")
    print("=" * 70)
    print()
    
    success = migrate_demo_to_user()
    
    if not success:
        print("\nLa migracion no se completo correctamente")
        exit(1)
