# 🚀 Sistema de Login y Registro - Alta Disponibilidad

## Descripción
Aplicación web completa con sistema de autenticación usando FastAPI (backend) y HTML/JavaScript (frontend).

**🛡️ NUEVO: Sistema robusto con supervisión automática y recuperación ante fallos**
**🆕 API REST completa para gestión de clientes, obras, productos y registros**

## ⚡ Inicio Rápido (RECOMENDADO)

**La forma más fácil y segura:**

```cmd
start_server.bat
```

✅ Supervisión automática | ✅ Reinicio automático | ✅ Logging completo | ✅ Hot-reload

---

## Características

### Sistema de Autenticación
- ✅ Registro de usuarios con validación robusta
- ✅ Login con autenticación segura
- ✅ Contraseñas hasheadas con bcrypt
- ✅ Gestión de perfil de usuario
- ✅ Validación en tiempo real en el frontend

### Gestión de Datos (NUEVO)
- ✅ **CRUD completo de Clientes**: Crea, consulta, actualiza y elimina clientes
- ✅ **CRUD completo de Obras**: Gestiona proyectos y obras
- ✅ **CRUD completo de Productos**: Catálogo de productos con precios
- ✅ **CRUD completo de Registros**: Registros de ventas/cobros con detalles
- ✅ **Reportes y Estadísticas**: Análisis por obra, fecha, totales agregados
- ✅ **Filtros avanzados**: Por obra, rango de fechas, estado

### Infraestructura
- ✅ Base de datos SQLite con relaciones
- ✅ Aislamiento de datos por usuario
- ✅ Diseño moderno y responsivo con Bootstrap 5
- 🆕 **Supervisión automática del servidor**
- 🆕 **Reinicio automático en caso de fallos**
- 🆕 **Sistema de logging completo**
- 🆕 **Health checks y monitoring**
- 🆕 **Middleware de error handling global**
- 🆕 **Retry logic en conexiones DB**

## API REST

### Endpoints Disponibles

#### Autenticación
- `POST /api/login` - Iniciar sesión
- `POST /api/register` - Registrar nuevo usuario
- `GET /api/user` - Obtener datos del usuario

#### Clientes
- `GET /api/clientes` - Listar clientes
- `POST /api/clientes` - Crear cliente
- `PUT /api/clientes/{id}` - Actualizar cliente
- `DELETE /api/clientes/{id}` - Eliminar cliente

#### Obras
- `GET /api/obras` - Listar obras
- `POST /api/obras` - Crear obra
- `PUT /api/obras/{id}` - Actualizar obra
- `DELETE /api/obras/{id}` - Eliminar obra

#### Productos
- `GET /api/productos` - Listar productos
- `POST /api/productos` - Crear producto
- `PUT /api/productos/{id}` - Actualizar producto
- `DELETE /api/productos/{id}` - Eliminar producto

#### Registros
- `GET /api/registros` - Listar registros (con filtros)
- `POST /api/registros` - Crear registro
- `PUT /api/registros/{id}` - Actualizar registro
- `DELETE /api/registros/{id}` - Eliminar registro

#### Reportes
- `GET /api/reportes` - Generar estadísticas y reportes

📖 **Documentación completa**: Ver [API_ENDPOINTS.md](API_ENDPOINTS.md)

## Requisitos
- Python 3.8 o superior
- Navegador web moderno

## Instalación

### 1. Instalar dependencias del backend

```powershell
python -m pip install -r backend\requirements.txt
```

Las dependencias incluyen:
- fastapi
- uvicorn[standard]
- python-multipart
- jinja2
- bcrypt

### 2. Iniciar el servidor backend

**🌟 OPCIÓN RECOMENDADA - Con Supervisión Automática:**

```cmd
start_server.bat          # Desarrollo (con hot-reload)
start_server_production.bat   # Producción
```

**Ventajas:**
- Reinicio automático si el servidor se cae
- Logging completo en `backend.log`
- Protección contra loops infinitos
- Mejor manejo de errores

**Opción Manual (tradicional):**

```powershell
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

El servidor estará disponible en: http://127.0.0.1:8000

**Health Check:**
```
GET http://127.0.0.1:8000/health
GET http://127.0.0.1:8000/api/status
```

### 3. Abrir el frontend

Opción recomendada: visita http://127.0.0.1:8000 y el backend servirá `index.html` del frontend.

Alternativa: abre el archivo `frontend\index.html` en tu navegador (usará la API en `http://127.0.0.1:8000`).

## Uso

### Registrar una nueva cuenta

1. Desde la página de login, haz clic en "¿No tienes cuenta? Registrate aquí"
2. Completa el formulario con:
   - **Correo**: debe ser un correo válido
   - **Usuario**: mínimo 3 caracteres
   - **Fecha de nacimiento**: selecciona día, mes y año
   - **Contraseña**: debe cumplir con:
     - Tener mayúsculas y minúsculas
     - Incluir números
     - Más de 6 caracteres
   - **Confirmar contraseña**: debe coincidir con la contraseña
3. El botón "Crear cuenta" se habilitará solo cuando todos los criterios se cumplan
4. Tras registro exitoso, serás redirigido automáticamente al login

### Iniciar sesión

1. Ingresa tu usuario y contraseña
2. Haz clic en "Iniciar Sesión"
3. Si las credenciales son correctas, verás un mensaje de éxito

## Estructura del Proyecto

```
.
├── backend/
│   ├── app.py                 # Aplicación FastAPI principal
│   └── requirements.txt       # Dependencias Python
├── frontend/
│   ├── index.html            # Página de login
│   └── register.html         # Página de registro
├── backend/templates/        # Plantillas Jinja2 (opcional)
│   └── login.html
└── backend/users.db          # Base de datos SQLite (se crea automáticamente)
```

## Base de Datos

La base de datos SQLite (`backend/users.db`) se crea automáticamente al iniciar el servidor por primera vez.

### Esquema de la tabla `users`:
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `email`: TEXT UNIQUE NOT NULL
- `username`: TEXT UNIQUE NOT NULL
- `birthdate`: TEXT NOT NULL
- `password_hash`: TEXT NOT NULL
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

## Seguridad

- ✅ Las contraseñas nunca se guardan en texto plano
- ✅ Se usa bcrypt para hashear contraseñas con salt automático
- ✅ Validación de unicidad para usuarios y correos
- ✅ CORS configurado para desarrollo local
- ⚠️ **Nota**: En producción, configura CORS con orígenes específicos

## Solución de Problemas

### Verificar que el backend está activo
Abre en el navegador:

```
http://127.0.0.1:8000/health
```

Debe responder con:

```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

### Ver los logs

```powershell
# En tiempo real
Get-Content backend.log -Wait

# Últimas 50 líneas
Get-Content backend.log -Tail 50
```

### Probar la API

**Script de prueba automático**:
```cmd
python test_api.py
```

**Prueba manual**:
```bash
# Login
curl -X POST http://127.0.0.1:8000/api/login -d "username=demo&password=Demo1234"

# Obtener clientes
curl "http://127.0.0.1:8000/api/clientes?username=demo"
```

---

## 📚 Documentación Adicional

- **[API_ENDPOINTS.md](API_ENDPOINTS.md)** - Documentación completa de todos los endpoints de la API
- **[PUNTOS_COMPLETADOS.md](PUNTOS_COMPLETADOS.md)** - Lista de funcionalidades completadas
- **[SISTEMA_ALTA_DISPONIBILIDAD.md](SISTEMA_ALTA_DISPONIBILIDAD.md)** - Guía del sistema de supervisión
- **[RESUMEN_MEJORAS.md](RESUMEN_MEJORAS.md)** - Historial de mejoras implementadas

---

## 🗄️ Estructura de la Base de Datos

El sistema utiliza SQLite con las siguientes tablas:

- **users** - Usuarios del sistema (autenticación)
- **clientes** - Información de clientes
- **obras** - Proyectos/obras gestionados
- **productos** - Catálogo de productos con precios
- **registros** - Registros de ventas/cobros con detalles

Todas las tablas tienen relación con `users` para aislar los datos por usuario.

---

## 🎉 ¡Listo para Usar!

El sistema está completamente funcional con:
- ✅ Backend completo con API REST
- ✅ Frontend con interfaz moderna
- ✅ Base de datos con persistencia
- ✅ Documentación completa
- ✅ Pruebas automatizadas
- ✅ Sistema de supervisión y logging

**Versión**: 2.0.0  
**Última actualización**: 6 de Enero de 2026

### Error: "ModuleNotFoundError: No module named 'bcrypt'"
**Solución**: Instala bcrypt
```powershell
python -m pip install bcrypt
```

### Error: "El usuario o correo ya existe"
**Solución**: El usuario o correo ya está registrado. Usa credenciales diferentes.

### Error: "Error al conectar con el servidor"
**Solución**: Verifica que el backend esté corriendo en http://127.0.0.1:8000

### La página no muestra datos
**Solución**: Abre la consola del navegador (F12) para ver errores JavaScript.

### No puedo iniciar sesión después de registrarme
- Asegúrate de que el backend esté corriendo y accesible en `http://127.0.0.1:8000`.
- Revisa que el formulario de login use exactamente tu `username` y `password` (el sistema no usa email para iniciar sesión).
- La base de datos ahora se guarda en `backend/users.db`, por lo que no depende del directorio desde el que ejecutes el servidor.
- Prueba registrar un usuario nuevo desde `register.html` y luego iniciar sesión con esos mismos datos.

## Desarrollo

### Ejecutar en modo desarrollo
El flag `--reload` hace que el servidor se reinicie automáticamente al detectar cambios en el código.

### Ver la base de datos
Puedes usar cualquier visor de SQLite para explorar `backend/users.db`:
- DB Browser for SQLite
- SQLite Studio
- Extensión SQLite Viewer para VS Code

## Próximos Pasos Sugeridos

1. Implementar sesiones con JWT o cookies
2. Añadir recuperación de contraseña
3. Implementar panel de usuario (dashboard)
4. Añadir validación de correo electrónico
5. Implementar límite de intentos de login
6. Añadir logs de auditoría
7. Migrar a PostgreSQL para producción

## Tecnologías Utilizadas

- **Backend**: FastAPI, SQLite, bcrypt
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5
- **Servidor**: Uvicorn
- **Seguridad**: bcrypt para hashing de contraseñas

## Licencia
Este proyecto es de código abierto para fines educativos.
