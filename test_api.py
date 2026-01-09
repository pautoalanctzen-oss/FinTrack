"""
Script de prueba para verificar todos los endpoints de la API
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"
USERNAME = "demo"
PASSWORD = "Demo1234"

def test_login():
    """Prueba el endpoint de login"""
    print("\n=== Probando Login ===")
    response = requests.post(f"{BASE_URL}/api/login", data={
        "username": USERNAME,
        "password": PASSWORD
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_clientes():
    """Prueba los endpoints de clientes"""
    print("\n=== Probando Clientes ===")
    
    # Obtener clientes
    print("\n1. GET /api/clientes")
    response = requests.get(f"{BASE_URL}/api/clientes", params={"username": USERNAME})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Crear cliente
    print("\n2. POST /api/clientes")
    response = requests.post(f"{BASE_URL}/api/clientes", data={
        "username": USERNAME,
        "nombre": "Cliente de Prueba",
        "cedula": "12345678",
        "obra": "Obra Test",
        "estado": "activo",
        "fecha": "2025-12-17"
    })
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")
    
    if response.status_code == 200:
        cliente_id = result.get("id")
        
        # Actualizar cliente
        print(f"\n3. PUT /api/clientes/{cliente_id}")
        response = requests.put(f"{BASE_URL}/api/clientes/{cliente_id}", data={
            "username": USERNAME,
            "nombre": "Cliente Actualizado",
            "cedula": "12345678",
            "obra": "Obra Test",
            "estado": "activo",
            "fecha": "2025-12-17"
        })
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Eliminar cliente
        print(f"\n4. DELETE /api/clientes/{cliente_id}")
        response = requests.delete(f"{BASE_URL}/api/clientes/{cliente_id}", params={"username": USERNAME})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

def test_obras():
    """Prueba los endpoints de obras"""
    print("\n=== Probando Obras ===")
    
    # Obtener obras
    print("\n1. GET /api/obras")
    response = requests.get(f"{BASE_URL}/api/obras", params={"username": USERNAME})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Crear obra
    print("\n2. POST /api/obras")
    response = requests.post(f"{BASE_URL}/api/obras", data={
        "username": USERNAME,
        "nombre": "Obra de Prueba",
        "ubicacion": "Ciudad Test",
        "estado": "activa"
    })
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")
    
    if response.status_code == 200:
        obra_id = result.get("id")
        
        # Actualizar obra
        print(f"\n3. PUT /api/obras/{obra_id}")
        response = requests.put(f"{BASE_URL}/api/obras/{obra_id}", data={
            "username": USERNAME,
            "nombre": "Obra Actualizada",
            "ubicacion": "Ciudad Test 2",
            "estado": "activa"
        })
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Eliminar obra
        print(f"\n4. DELETE /api/obras/{obra_id}")
        response = requests.delete(f"{BASE_URL}/api/obras/{obra_id}", params={"username": USERNAME})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

def test_productos():
    """Prueba los endpoints de productos"""
    print("\n=== Probando Productos ===")
    
    # Obtener productos
    print("\n1. GET /api/productos")
    response = requests.get(f"{BASE_URL}/api/productos", params={"username": USERNAME})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Crear producto
    print("\n2. POST /api/productos")
    response = requests.post(f"{BASE_URL}/api/productos", data={
        "username": USERNAME,
        "nombre": "Producto de Prueba",
        "precio": 50.0
    })
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")
    
    if response.status_code == 200:
        producto_id = result.get("id")
        
        # Actualizar producto
        print(f"\n3. PUT /api/productos/{producto_id}")
        response = requests.put(f"{BASE_URL}/api/productos/{producto_id}", data={
            "username": USERNAME,
            "nombre": "Producto Actualizado",
            "precio": 75.0
        })
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Eliminar producto
        print(f"\n4. DELETE /api/productos/{producto_id}")
        response = requests.delete(f"{BASE_URL}/api/productos/{producto_id}", params={"username": USERNAME})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

def test_registros():
    """Prueba los endpoints de registros"""
    print("\n=== Probando Registros ===")
    
    # Obtener registros
    print("\n1. GET /api/registros")
    response = requests.get(f"{BASE_URL}/api/registros", params={"username": USERNAME})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Crear registro
    print("\n2. POST /api/registros")
    registro_data = {
        "username": USERNAME,
        "fecha": "2025-12-17",
        "obra": "Obra Central",
        "totalCantidad": 10,
        "totalCobrar": 500.0,
        "totalPagado": 300.0,
        "status": "parcial",
        "clientesAdicionales": ["Cliente A", "Cliente B"],
        "detalles": [
            {"producto": "Producto 1", "cantidad": 5, "precio": 50.0},
            {"producto": "Producto 2", "cantidad": 5, "precio": 50.0}
        ]
    }
    response = requests.post(f"{BASE_URL}/api/registros", 
                            json=registro_data,
                            headers={"Content-Type": "application/json"})
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")
    
    if response.status_code == 200:
        registro_id = result.get("id")
        
        # Actualizar registro
        print(f"\n3. PUT /api/registros/{registro_id}")
        registro_data["totalPagado"] = 500.0
        registro_data["status"] = "pagado"
        response = requests.put(f"{BASE_URL}/api/registros/{registro_id}", 
                               json=registro_data,
                               headers={"Content-Type": "application/json"})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Eliminar registro
        print(f"\n4. DELETE /api/registros/{registro_id}")
        response = requests.delete(f"{BASE_URL}/api/registros/{registro_id}", params={"username": USERNAME})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

def test_reportes():
    """Prueba el endpoint de reportes"""
    print("\n=== Probando Reportes ===")
    response = requests.get(f"{BASE_URL}/api/reportes", params={
        "username": USERNAME,
        "fecha_inicio": "2025-12-01",
        "fecha_fin": "2025-12-31"
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_health():
    """Prueba los endpoints de monitoreo"""
    print("\n=== Probando Health Checks ===")
    
    print("\n1. GET /health")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    print("\n2. GET /api/status")
    response = requests.get(f"{BASE_URL}/api/status")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    print("=" * 60)
    print("PRUEBAS DE API - Sistema de Gestión")
    print("=" * 60)
    
    try:
        # Primero verificar que el servidor está corriendo
        test_health()
        
        # Luego probar login
        if test_login():
            # Si el login es exitoso, probar el resto de endpoints
            test_clientes()
            test_obras()
            test_productos()
            test_registros()
            test_reportes()
        else:
            print("\n❌ Error: No se pudo autenticar. Verifica las credenciales.")
        
        print("\n" + "=" * 60)
        print("✅ Pruebas completadas")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: No se pudo conectar al servidor.")
        print("Asegúrate de que el servidor esté corriendo en http://127.0.0.1:8000")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
