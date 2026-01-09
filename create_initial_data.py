"""
Script simplificado para crear datos iniciales mínimos en Render
"""
import requests
import time

RENDER_API = "https://aplicaci-n-mi.onrender.com"
USERNAME = "Panchita's Catering"

def wake_up_server():
    """Despierta el servidor de Render"""
    print("Despertando servidor de Render...")
    try:
        response = requests.get(f"{RENDER_API}/health", timeout=30)
        print(f"✓ Servidor activo (código: {response.status_code})")
        return True
    except Exception as e:
        print(f"✗ Error al conectar: {e}")
        return False

def create_initial_data():
    """Crea datos iniciales básicos"""
    print(f"\nCreando datos iniciales para {USERNAME}...")
    
    # Crear algunas obras principales
    obras = [
        {"nombre": "Jardineros Vista al Río", "ubicacion": "Vista al Río", "estado": "activa"},
        {"nombre": "Aires Norte", "ubicacion": "Norte", "estado": "activa"},
        {"nombre": "Puntilla", "ubicacion": "Puntilla", "estado": "activa"}
    ]
    
    print("\nCreando obras...")
    for obra in obras:
        try:
            response = requests.post(
                f"{RENDER_API}/api/obras",
                data={
                    "username": USERNAME,
                    **obra
                },
                timeout=30
            )
            if response.status_code == 200:
                print(f"  ✓ {obra['nombre']}")
            else:
                print(f"  ✗ {obra['nombre']}: {response.status_code} - {response.text[:100]}")
            time.sleep(0.5)  # Pequeña pausa entre requests
        except Exception as e:
            print(f"  ✗ {obra['nombre']}: {e}")
    
    # Crear algunos productos básicos
    productos = [
        {"nombre": "Desayuno", "precio": 3.50},
        {"nombre": "Almuerzo", "precio": 4.00}
    ]
    
    print("\nCreando productos...")
    for producto in productos:
        try:
            response = requests.post(
                f"{RENDER_API}/api/productos",
                data={
                    "username": USERNAME,
                    **producto
                },
                timeout=30
            )
            if response.status_code == 200:
                print(f"  ✓ {producto['nombre']} - ${producto['precio']}")
            else:
                print(f"  ✗ {producto['nombre']}: {response.status_code}")
            time.sleep(0.5)
        except Exception as e:
            print(f"  ✗ {producto['nombre']}: {e}")
    
    # Crear algunos clientes básicos
    clientes = [
        {"nombre": "Administrador", "cedula": "0000000000", "obra": "General", "estado": "activo"},
        {"nombre": "Reyes", "cedula": "", "obra": "Jardineros Vista al Río", "estado": "activo"}
    ]
    
    print("\nCreando clientes...")
    for cliente in clientes:
        try:
            response = requests.post(
                f"{RENDER_API}/api/clientes",
                data={
                    "username": USERNAME,
                    **cliente
                },
                timeout=30
            )
            if response.status_code == 200:
                print(f"  ✓ {cliente['nombre']}")
            else:
                print(f"  ✗ {cliente['nombre']}: {response.status_code}")
            time.sleep(0.5)
        except Exception as e:
            print(f"  ✗ {cliente['nombre']}: {e}")

def main():
    print("=" * 70)
    print("CREANDO DATOS INICIALES EN RENDER")
    print("=" * 70)
    
    if wake_up_server():
        time.sleep(2)  # Dar tiempo al servidor
        create_initial_data()
        print("\n" + "=" * 70)
        print("✓ DATOS INICIALES CREADOS")
        print("=" * 70)
        print("\nAhora puedes:")
        print("1. Ir a: https://aplicaci-n-mi.vercel.app")
        print(f"2. Iniciar sesión con: {USERNAME}")
        print("3. Agregar más datos desde la interfaz")
    else:
        print("\n✗ No se pudo conectar al servidor")

if __name__ == "__main__":
    main()
