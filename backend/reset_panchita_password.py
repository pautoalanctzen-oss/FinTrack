import sqlite3
import bcrypt

DB_PATH = "users.db"
password = "Panchita2024!"

# Hash de la contraseña
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Actualizar en la base de datos
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute(
    "UPDATE users SET password_hash = ? WHERE username = ?",
    (password_hash, "Panchita's Catering")
)

conn.commit()
affected = cursor.rowcount
conn.close()

print(f"Contraseña actualizada para 'Panchita's Catering'")
print(f"Filas afectadas: {affected}")
print(f"Nueva contraseña: {password}")
print(f"Hash generado: {password_hash}")
