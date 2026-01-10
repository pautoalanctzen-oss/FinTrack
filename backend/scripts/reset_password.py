"""Script para resetear o verificar contraseñas de usuarios."""
import sqlite3
import bcrypt
import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "users.db")


def list_users():
    """Lista todos los usuarios."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email FROM users ORDER BY id")
    users = cursor.fetchall()
    conn.close()
    
    print("\n=== Usuarios en la base de datos ===")
    for user in users:
        print(f"ID: {user['id']}, Username: {user['username']}, Email: {user['email']}")
    print()
    return users


def verify_password(username, password):
    """Verifica si una contraseña es correcta para un usuario."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        print(f"❌ Usuario '{username}' no encontrado")
        return False
    
    password_hash = row["password_hash"]
    if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
        print(f"✅ Contraseña correcta para usuario '{username}'")
        return True
    else:
        print(f"❌ Contraseña incorrecta para usuario '{username}'")
        return False


def reset_password(username, new_password):
    """Resetea la contraseña de un usuario."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verificar que el usuario existe
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if not cursor.fetchone():
        print(f"❌ Usuario '{username}' no encontrado")
        conn.close()
        return False
    
    # Hashear nueva contraseña
    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Actualizar contraseña
    cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (password_hash, username))
    conn.commit()
    conn.close()
    
    print(f"✅ Contraseña actualizada exitosamente para usuario '{username}'")
    print(f"   Nueva contraseña: {new_password}")
    return True


def interactive_mode():
    """Modo interactivo para gestionar contraseñas."""
    list_users()
    
    print("Opciones:")
    print("1. Verificar contraseña")
    print("2. Resetear contraseña")
    print("3. Salir")
    
    choice = input("\nSelecciona una opción (1-3): ").strip()
    
    if choice == "1":
        username = input("Username: ").strip()
        password = input("Contraseña a verificar: ").strip()
        verify_password(username, password)
    
    elif choice == "2":
        username = input("Username: ").strip()
        new_password = input("Nueva contraseña: ").strip()
        confirm = input("Confirmar nueva contraseña: ").strip()
        
        if new_password != confirm:
            print("❌ Las contraseñas no coinciden")
            return
        
        if len(new_password) < 6:
            print("❌ La contraseña debe tener al menos 6 caracteres")
            return
        
        reset_password(username, new_password)
    
    elif choice == "3":
        print("Saliendo...")
        return
    
    else:
        print("❌ Opción inválida")


if __name__ == "__main__":
    print("=== Gestión de Contraseñas ===")
    print(f"Base de datos: {DB_PATH}\n")
    
    # Si se pasan argumentos por línea de comandos
    if len(sys.argv) >= 3:
        if sys.argv[1] == "verify":
            username = sys.argv[2]
            password = sys.argv[3] if len(sys.argv) > 3 else input("Contraseña: ")
            verify_password(username, password)
        elif sys.argv[1] == "reset":
            username = sys.argv[2]
            new_password = sys.argv[3] if len(sys.argv) > 3 else input("Nueva contraseña: ")
            reset_password(username, new_password)
        else:
            print("Uso: python reset_password.py [verify|reset] <username> [password]")
    else:
        # Modo interactivo
        interactive_mode()
