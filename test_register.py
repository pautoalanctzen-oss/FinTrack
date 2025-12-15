"""Script de prueba para verificar el registro de usuarios."""
import requests

BASE_URL = "http://127.0.0.1:8000"

# Datos de prueba
data = {
    "email": "test@example.com",
    "username": "testuser",
    "birthdate": "2000-01-15",
    "password": "Test123456",
    "confirm_password": "Test123456"
}

print("Enviando solicitud de registro...")
print(f"Datos: {data}")

try:
    response = requests.post(f"{BASE_URL}/api/register", data=data)
    print(f"\nCódigo de respuesta: {response.status_code}")
    print(f"Respuesta JSON: {response.json()}")
    
    if response.status_code == 200:
        print("\n✓ Registro exitoso!")
    else:
        print(f"\n✗ Error en el registro: {response.json().get('message', 'Error desconocido')}")
        
except Exception as e:
    print(f"\n✗ Error al conectar con el servidor: {e}")
