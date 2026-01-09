# 📡 Documentación de API - Endpoints

## Descripción General

Este documento describe todos los endpoints disponibles en el backend de la aplicación.

**Base URL**: `http://127.0.0.1:8000` (desarrollo) o tu URL de producción

---

## 🔐 Autenticación

### POST `/api/login`
Inicia sesión con credenciales de usuario.

**Parámetros (Form Data)**:
- `username` (string, requerido): Nombre de usuario
- `password` (string, requerido): Contraseña

**Respuesta exitosa**:
```json
{
  "username": "demo",
  "authenticated": true,
  "message": "Autenticado correctamente"
}
```

### POST `/api/register`
Registra un nuevo usuario.

**Parámetros (Form Data)**:
- `email` (string, requerido): Correo electrónico válido
- `username` (string, requerido): Nombre de usuario (mínimo 3 caracteres)
- `birthdate` (string, requerido): Fecha de nacimiento (formato: YYYY-MM-DD)
- `password` (string, requerido): Contraseña (mínimo 6 caracteres)
- `confirm_password` (string, requerido): Confirmación de contraseña

**Respuesta exitosa**:
```json
{
  "success": true,
  "message": "Registro exitoso"
}
```

---

## 👤 Perfil de Usuario

### GET `/api/user`
Obtiene información del usuario.

**Parámetros (Query)**:
- `username` (string, requerido)

**Respuesta**:
```json
{
  "email": "demo@example.com",
  "username": "demo",
  "birthdate": "2000-01-01",
  "created_at": "2025-12-17 21:58:47"
}
```

### POST `/api/settings/update-email`
Actualiza el correo del usuario.

**Parámetros (Form Data)**:
- `username` (string, requerido)
- `email` (string, requerido)

### POST `/api/settings/update-username`
Actualiza el nombre de usuario.

**Parámetros (Form Data)**:
- `username` (string, requerido): Usuario actual
- `new_username` (string, requerido): Nuevo nombre de usuario

### POST `/api/settings/update-password`
Actualiza la contraseña del usuario.

**Parámetros (Form Data)**:
- `username` (string, requerido)
- `current_password` (string, requerido)
- `new_password` (string, requerido)
- `confirm_password` (string, requerido)

---

## 👥 Clientes

### GET `/api/clientes`
Obtiene todos los clientes del usuario.

**Parámetros (Query)**:
- `username` (string, requerido)

**Respuesta**:
```json
{
  "clientes": [
    {
      "id": 1,
      "nombre": "Cliente Uno",
      "cedula": "0101",
      "obra": "Obra Central",
      "estado": "activo",
      "fecha": "2025-12-17",
      "created_at": "2025-12-17 21:58:47"
    }
  ]
}
```

### POST `/api/clientes`
Crea un nuevo cliente.

**Parámetros (Form Data)**:
- `username` (string, requerido)
- `nombre` (string, requerido)
- `cedula` (string, opcional)
- `obra` (string, opcional)
- `estado` (string, opcional, default: "activo")
- `fecha` (string, opcional, formato: YYYY-MM-DD)

**Respuesta**:
```json
{
  "success": true,
  "id": 1
}
```

### PUT `/api/clientes/{cliente_id}`
Actualiza un cliente existente.

**Parámetros (Form Data)**:
- `username` (string, requerido)
- `nombre` (string, requerido)
- `cedula` (string, opcional)
- `obra` (string, opcional)
- `estado` (string, opcional)
- `fecha` (string, opcional)

### DELETE `/api/clientes/{cliente_id}`
Elimina un cliente.

**Parámetros (Query)**:
- `username` (string, requerido)

---

## 🏗️ Obras

### GET `/api/obras`
Obtiene todas las obras del usuario.

**Parámetros (Query)**:
- `username` (string, requerido)

**Respuesta**:
```json
{
  "obras": [
    {
      "id": 1,
      "nombre": "Obra Central",
      "ubicacion": "Ciudad",
      "estado": "activa",
      "created_at": "2025-12-17 21:58:47"
    }
  ]
}
```

### POST `/api/obras`
Crea una nueva obra.

**Parámetros (Form Data)**:
- `username` (string, requerido)
- `nombre` (string, requerido)
- `ubicacion` (string, opcional)
- `estado` (string, opcional, default: "activa")

### PUT `/api/obras/{obra_id}`
Actualiza una obra existente.

**Parámetros (Form Data)**:
- `username` (string, requerido)
- `nombre` (string, requerido)
- `ubicacion` (string, opcional)
- `estado` (string, opcional)

### DELETE `/api/obras/{obra_id}`
Elimina una obra.

**Parámetros (Query)**:
- `username` (string, requerido)

---

## 📦 Productos

### GET `/api/productos`
Obtiene todos los productos del usuario.

**Parámetros (Query)**:
- `username` (string, requerido)

**Respuesta**:
```json
{
  "productos": [
    {
      "id": 1,
      "nombre": "Producto A",
      "precio": 25.0,
      "created_at": "2025-12-17 21:58:47"
    }
  ]
}
```

### POST `/api/productos`
Crea un nuevo producto.

**Parámetros (Form Data)**:
- `username` (string, requerido)
- `nombre` (string, requerido)
- `precio` (float, requerido)

### PUT `/api/productos/{producto_id}`
Actualiza un producto existente.

**Parámetros (Form Data)**:
- `username` (string, requerido)
- `nombre` (string, requerido)
- `precio` (float, requerido)

### DELETE `/api/productos/{producto_id}`
Elimina un producto.

**Parámetros (Query)**:
- `username` (string, requerido)

---

## 📝 Registros

### GET `/api/registros`
Obtiene todos los registros del usuario con filtros opcionales.

**Parámetros (Query)**:
- `username` (string, requerido)
- `obra` (string, opcional): Filtrar por obra
- `fecha_inicio` (string, opcional, formato: YYYY-MM-DD)
- `fecha_fin` (string, opcional, formato: YYYY-MM-DD)

**Respuesta**:
```json
{
  "registros": [
    {
      "id": 1,
      "fecha": "2025-12-17",
      "obra": "Obra Central",
      "totalCantidad": 5,
      "totalCobrar": 125.0,
      "totalPagado": 125.0,
      "status": "pagado",
      "clientesAdicionales": [],
      "detalles": [],
      "created_at": "2025-12-17 21:58:47"
    }
  ]
}
```

### POST `/api/registros`
Crea un nuevo registro.

**Parámetros (JSON Body)**:
```json
{
  "username": "demo",
  "fecha": "2025-12-17",
  "obra": "Obra Central",
  "totalCantidad": 5,
  "totalCobrar": 125.0,
  "totalPagado": 100.0,
  "status": "parcial",
  "clientesAdicionales": ["Cliente 1", "Cliente 2"],
  "detalles": [
    {
      "producto": "Producto A",
      "cantidad": 3,
      "precio": 25.0
    }
  ]
}
```

**Respuesta**:
```json
{
  "success": true,
  "id": 1
}
```

### PUT `/api/registros/{registro_id}`
Actualiza un registro existente.

**Parámetros (JSON Body)**: Igual que POST

### DELETE `/api/registros/{registro_id}`
Elimina un registro.

**Parámetros (Query)**:
- `username` (string, requerido)

---

## 📊 Reportes y Estadísticas

### GET `/api/reportes`
Genera estadísticas y reportes basados en los registros.

**Parámetros (Query)**:
- `username` (string, requerido)
- `obra` (string, opcional): Filtrar por obra
- `fecha_inicio` (string, opcional, formato: YYYY-MM-DD)
- `fecha_fin` (string, opcional, formato: YYYY-MM-DD)

**Respuesta**:
```json
{
  "totales": {
    "totalCobrar": 500.0,
    "totalCobrado": 350.0,
    "totalPendiente": 150.0,
    "totalCantidad": 20,
    "totalRegistros": 5
  },
  "porObra": {
    "Obra Central": {
      "totalCobrar": 500.0,
      "totalCobrado": 350.0,
      "totalPendiente": 150.0,
      "totalCantidad": 20
    }
  },
  "porFecha": {
    "2025-12-17": {
      "totalCobrar": 125.0,
      "totalCobrado": 125.0,
      "totalPendiente": 0.0,
      "totalCantidad": 5
    }
  },
  "registros": [...]
}
```

---

## 🔍 Monitoreo

### GET `/health`
Verifica el estado del servidor y la base de datos.

**Respuesta exitosa**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-17T21:58:47.123456",
  "database": "connected",
  "version": "1.0.0"
}
```

### GET `/api/status`
Estado detallado del sistema con estadísticas.

**Respuesta**:
```json
{
  "status": "ok",
  "timestamp": "2025-12-17T21:58:47.123456",
  "services": {
    "database": "healthy",
    "api": "healthy"
  },
  "stats": {
    "total_users": 5
  }
}
```

---

## 📝 Notas Importantes

1. **Autenticación**: Todos los endpoints que requieren `username` verifican que el usuario existe antes de realizar operaciones.

2. **Aislamiento de datos**: Cada usuario solo puede acceder a sus propios datos (clientes, obras, productos, registros).

3. **Validaciones**:
   - Correos deben ser válidos
   - Usuarios deben tener mínimo 3 caracteres
   - Contraseñas deben cumplir requisitos de seguridad

4. **Formatos de fecha**: Usar siempre formato ISO (YYYY-MM-DD)

5. **Estados**:
   - Clientes/Obras: "activo" o "inactivo"
   - Registros: "pagado", "parcial", o "pendiente"

6. **Errores comunes**:
   - `404`: Usuario, cliente, obra, producto o registro no encontrado
   - `400`: Datos inválidos o ya existentes
   - `500`: Error interno del servidor

---

## 🚀 Próximos Pasos

Para integrar el frontend con el backend:

1. Reemplazar las funciones de localStorage con llamadas a estos endpoints
2. Agregar manejo de sesión (guardar username en sessionStorage)
3. Implementar manejo de errores con mensajes al usuario
4. Considerar agregar tokens JWT para mayor seguridad

---

## 📞 Soporte

Para reportar problemas o solicitar nuevas funcionalidades, revisa los logs en `backend.log`.
