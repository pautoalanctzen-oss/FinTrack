# Sistema de Login y Registro - Aplicación Web

## Descripción
Aplicación web completa con sistema de autenticación usando FastAPI (backend) y HTML/JavaScript (frontend).

## Características
- ✅ Registro de usuarios con validación robusta
- ✅ Login con autenticación segura
- ✅ Contraseñas hasheadas con bcrypt
- ✅ Base de datos SQLite
- ✅ Validación en tiempo real en el frontend
- ✅ Diseño moderno y responsivo con Bootstrap 5

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

```powershell
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

O si estás usando el entorno virtual:

```powershell
& ".\.venv\Scripts\python.exe" -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

El servidor estará disponible en: http://127.0.0.1:8000

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

```
{ "status": "ok" }
```

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
