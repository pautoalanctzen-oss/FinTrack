from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from datetime import date, datetime
import sqlite3
import bcrypt
from contextlib import contextmanager
import os
import re
import logging
import sys
import traceback
from typing import Union
import time

# =======================
# CONFIGURACIÓN DE LOGGING
# =======================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sistema de Login y Registro", version="1.0.0")

# Base de datos SQLite (ruta absoluta para evitar inconsistencias por CWD)
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


@contextmanager
def get_db():
    """Context manager para manejar conexiones a la base de datos con retry logic."""
    max_retries = 3
    retry_delay = 0.5
    conn = None
    
    for attempt in range(max_retries):
        try:
            conn = sqlite3.connect(DB_PATH, timeout=10.0)
            conn.row_factory = sqlite3.Row
            # Test the connection
            conn.execute("SELECT 1")
            break
        except sqlite3.Error as e:
            logger.error(f"Error al conectar a DB (intento {attempt + 1}/{max_retries}): {e}")
            if conn:
                conn.close()
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.critical("No se pudo establecer conexión con la base de datos")
                raise
    
    try:
        yield conn
    except Exception as e:
        logger.error(f"Error durante operación de DB: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def init_db():
    """Inicializa la base de datos con todas las tablas necesarias."""
    try:
        logger.info("Inicializando base de datos...")
        with get_db() as conn:
            # Tabla de usuarios
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    birthdate TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de obras
            conn.execute("""
                CREATE TABLE IF NOT EXISTS obras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    nombre TEXT NOT NULL,
                    ubicacion TEXT,
                    estado TEXT DEFAULT 'activa',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Tabla de clientes
            conn.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    nombre TEXT NOT NULL,
                    cedula TEXT,
                    obra TEXT,
                    estado TEXT DEFAULT 'activo',
                    fecha TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Tabla de productos
            conn.execute("""
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    nombre TEXT NOT NULL,
                    precio REAL NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Tabla de registros
            conn.execute("""
                CREATE TABLE IF NOT EXISTS registros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    fecha TEXT,
                    obra TEXT,
                    totalCantidad INTEGER DEFAULT 0,
                    totalCobrar REAL DEFAULT 0,
                    totalPagado REAL DEFAULT 0,
                    status TEXT DEFAULT 'pendiente',
                    clientesAdicionales TEXT,
                    detalles TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            conn.commit()
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.critical(f"Error crítico al inicializar la base de datos: {e}")
        raise


# Inicializar DB al arrancar
init_db()


def ensure_demo_user():
    """Crea un usuario de prueba si no existe para facilitar el acceso.

    Usuario: demo
    Contraseña: Demo1234
    """
    try:
        email = "demo@example.com"
        username = "demo"
        birthdate = "2000-01-01"
        password_plain = "Demo1234"
        with get_db() as conn:
            cur = conn.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
            row = cur.fetchone()
            if row:
                logger.info("Usuario demo ya existe")
                return
            password_hash = bcrypt.hashpw(password_plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            conn.execute(
                "INSERT INTO users (email, username, birthdate, password_hash) VALUES (?, ?, ?, ?)",
                (email, username, birthdate, password_hash),
            )
            conn.commit()
            logger.info("Usuario demo creado exitosamente")
    except Exception as e:
        logger.error(f"Error al crear usuario demo: {e}")
        # No es crítico, no detenemos la app


# Asegurar usuario demo persistente
ensure_demo_user()

# Montar archivos estáticos del frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/frontend", StaticFiles(directory=frontend_path), name="frontend")

# Directorio de plantillas (para compatibilidad, aunque ahora usamos archivos estáticos)
templates = Jinja2Templates(directory="templates")

# =======================
# MIDDLEWARE DE ERROR HANDLING GLOBAL
# =======================
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    """Middleware que captura todas las excepciones no manejadas."""
    try:
        return await call_next(request)
    except Exception as exc:
        logger.error(f"Error no manejado en {request.method} {request.url.path}: {exc}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Error interno del servidor. El error ha sido registrado."},
        )

# CORS para permitir peticiones desde el frontend (archivo local o localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción, especifica orígenes permitidos
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def home():
    """Sirve la página de login (index.html)."""
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Bienvenido a la API"}


@app.get("/health")
async def health():
    """Endpoint de salud para verificar que el backend está activo."""
    try:
        # Verificar conexión a base de datos
        with get_db() as conn:
            conn.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )


@app.get("/api/status")
async def api_status():
    """Endpoint de status detallado para monitoring."""
    try:
        # Test DB
        db_healthy = False
        user_count = 0
        try:
            with get_db() as conn:
                result = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()
                user_count = result["count"]
                db_healthy = True
        except Exception as db_error:
            logger.error(f"DB health check error: {db_error}")
        
        return {
            "status": "ok" if db_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": "healthy" if db_healthy else "unhealthy",
                "api": "healthy"
            },
            "stats": {
                "total_users": user_count
            }
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": str(e)}
        )


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Procesa el formulario de login y vuelve a renderizar la plantilla con
    un mensaje de éxito/fracaso.
    """
    # Autenticación de ejemplo (solo demo)
    authenticated = (username == "admin" and password == "secret")
    message = "Autenticado correctamente" if authenticated else "Credenciales inválidas"

    context = {
        "request": request,
        "username": username,
        "authenticated": authenticated,
        "message": message,
    }
    return templates.TemplateResponse("login.html", context)


@app.post("/api/login")
async def api_login(username: str = Form(...), password: str = Form(...)):
    """API JSON para login desde el frontend - verifica contra DB."""
    try:
        logger.info(f"Intento de login para usuario: {username}")
        with get_db() as conn:
            cursor = conn.execute(
                "SELECT password_hash FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            
            if not row:
                logger.warning(f"Usuario no encontrado: {username}")
                return {"username": username, "authenticated": False, "message": "Credenciales inválidas"}
            
            # Verificar contraseña con bcrypt
            password_hash = row["password_hash"]
            if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                logger.info(f"Login exitoso para usuario: {username}")
                return {"username": username, "authenticated": True, "message": "Autenticado correctamente"}
            else:
                logger.warning(f"Contraseña incorrecta para usuario: {username}")
                return {"username": username, "authenticated": False, "message": "Credenciales inválidas"}
    except Exception as e:
        logger.error(f"Error en login para {username}: {e}")
        raise HTTPException(status_code=500, detail={"message": "Error al procesar login"})


@app.post("/api/register")
async def api_register(
    email: str = Form(...),
    username: str = Form(...),
    birthdate: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    """Registro: valida campos, crea usuario en DB con contraseña hasheada."""
    try:
        logger.info(f"Intento de registro para usuario: {username}")
        
        # Validaciones básicas
        if "@" not in email or "." not in email:
            raise HTTPException(status_code=400, detail={"message": "Correo inválido"})
        if len(username) < 3:
            raise HTTPException(status_code=400, detail={"message": "El usuario debe tener al menos 3 caracteres"})
        try:
            date.fromisoformat(birthdate)
        except Exception:
            raise HTTPException(status_code=400, detail={"message": "Fecha de nacimiento inválida (usa formato AAAA-MM-DD)"})
        if len(password) < 6:
            raise HTTPException(status_code=400, detail={"message": "La contraseña debe tener al menos 6 caracteres"})
        if password != confirm_password:
            raise HTTPException(status_code=400, detail={"message": "Las contraseñas no coinciden"})

        # Hashear contraseña con bcrypt
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Insertar usuario en la base de datos
        try:
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO users (email, username, birthdate, password_hash) VALUES (?, ?, ?, ?)",
                    (email, username, birthdate, password_hash)
                )
                conn.commit()
            logger.info(f"Usuario registrado exitosamente: {username}")
        except sqlite3.IntegrityError as e:
            logger.warning(f"Registro fallido - usuario o email duplicado: {username}")
            raise HTTPException(status_code=400, detail={"message": "El usuario o correo ya existe"})

        return {"success": True, "message": "Registro exitoso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en registro: {e}")
        raise HTTPException(status_code=500, detail={"message": "Error al procesar registro"})


# ----- Endpoints de Ajustes / Perfil -----
@app.get("/api/user")
async def get_user(username: str):
    """Obtiene datos públicos del usuario (email, username, birthdate, created_at)."""
    with get_db() as conn:
        cur = conn.execute("SELECT email, username, birthdate, created_at FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail={"message": "Usuario no encontrado"})
        return {"email": row["email"], "username": row["username"], "birthdate": row["birthdate"], "created_at": row["created_at"]}


@app.post("/api/settings/update-email")
async def update_email(username: str = Form(...), email: str = Form(...)):
    """Actualiza el correo del usuario con validación básica y unicidad."""
    if "@" not in email or "." not in email:
        raise HTTPException(status_code=400, detail={"message": "Correo inválido"})
    with get_db() as conn:
        # Verificar que usuario exista
        cur = conn.execute("SELECT id FROM users WHERE username = ?", (username,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail={"message": "Usuario no encontrado"})
        # Intentar actualizar
        try:
            conn.execute("UPDATE users SET email = ? WHERE username = ?", (email, username))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail={"message": "El correo ya está en uso"})
    return {"success": True}


@app.post("/api/settings/update-username")
async def update_username(username: str = Form(...), new_username: str = Form(...)):
    """Actualiza el nombre de usuario (mínimo 3 caracteres y único)."""
    if len(new_username) < 3:
        raise HTTPException(status_code=400, detail={"message": "El usuario debe tener al menos 3 caracteres"})
    with get_db() as conn:
        cur = conn.execute("SELECT id FROM users WHERE username = ?", (username,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail={"message": "Usuario no encontrado"})
        try:
            conn.execute("UPDATE users SET username = ? WHERE username = ?", (new_username, username))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail={"message": "El usuario ya existe"})
    return {"success": True}


@app.post("/api/settings/update-password")
async def update_password(
    username: str = Form(...),
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
):
    """Actualiza la contraseña del usuario verificando la actual y validando la nueva."""
    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail={"message": "Las contraseñas no coinciden"})
    # Validación de complejidad similar al front
    if len(new_password) <= 6 or not re.search(r"[a-z]", new_password) or not re.search(r"[A-Z]", new_password) or not re.search(r"\d", new_password):
        raise HTTPException(status_code=400, detail={"message": "La contraseña no cumple los criterios"})

    with get_db() as conn:
        cur = conn.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail={"message": "Usuario no encontrado"})
        # verificar contraseña actual
        if not bcrypt.checkpw(current_password.encode('utf-8'), row["password_hash"].encode('utf-8')):
            raise HTTPException(status_code=400, detail={"message": "La contraseña actual es incorrecta"})
        # actualizar
        new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        conn.execute("UPDATE users SET password_hash = ? WHERE username = ?", (new_hash, username))
        conn.commit()
    return {"success": True}


# ===============================================
# ENDPOINTS PARA CLIENTES
# ===============================================

@app.get("/api/clientes")
async def get_clientes(username: str):
    """Obtiene todos los clientes del usuario."""
    try:
        with get_db() as conn:
            # Obtener user_id
            user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if not user:
                raise HTTPException(status_code=404, detail={"message": "Usuario no encontrado"})
            
            # Obtener clientes
            cursor = conn.execute(
                "SELECT id, nombre, cedula, obra, estado, fecha, created_at FROM clientes WHERE user_id = ? ORDER BY created_at DESC",
                (user["id"],)
            )
            clientes = [dict(row) for row in cursor.fetchall()]
            return {"clientes": clientes}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener clientes: {e}")
        raise HTTPException(status_code=500, detail={"message": "Error al obtener clientes"})


@app.post("/api/clientes")
async def create_cliente(
    username: str = Form(...),
    nombre: str = Form(...),
    cedula: str = Form(None),
    obra: str = Form(None),
    estado: str = Form("activo"),
    fecha: str = Form(None)
):
    """Crea un nuevo cliente."""
    try:
        with get_db() as conn:
            # Obtener user_id
            user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if not user:
                raise HTTPException(status_code=404, detail={"message": "Usuario no encontrado"})
            
            # Insertar cliente
            cursor = conn.execute(
                "INSERT INTO clientes (user_id, nombre, cedula, obra, estado, fecha) VALUES (?, ?, ?, ?, ?, ?)",
                (user["id"], nombre, cedula, obra, estado, fecha)
            )
            conn.commit()
            
            return {"success": True, "id": cursor.lastrowid}
    except Exception as e:
        logger.error(f"Error al crear cliente: {e}")
        raise HTTPException(status_code=500, detail={"message": "Error al crear cliente"})


@app.put("/api/clientes/{cliente_id}")
async def update_cliente(
    cliente_id: int,
    username: str = Form(...),
    nombre: str = Form(...),
    cedula: str = Form(None),
    obra: str = Form(None),
    estado: str = Form("activo"),
    fecha: str = Form(None)
):
    """Actualiza un cliente existente."""
    try:
        with get_db() as conn:
            # Obtener user_id
            user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if not user:
                raise HTTPException(status_code=404, detail={"message": "Usuario no encontrado"})
            
            # Verificar que el cliente pertenece al usuario
            cliente = conn.execute(
                "SELECT id FROM clientes WHERE id = ? AND user_id = ?",
                (cliente_id, user["id"])
            ).fetchone()
            
            if not cliente:
                raise HTTPException(status_code=404, detail={"message": "Cliente no encontrado"})
            
            # Actualizar cliente
            conn.execute(
                "UPDATE clientes SET nombre = ?, cedula = ?, obra = ?, estado = ?, fecha = ? WHERE id = ?",
                (nombre, cedula, obra, estado, fecha, cliente_id)
            )
            conn.commit()
            
            return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar cliente: {e}")
        raise HTTPException(status_code=500, detail={"message": "Error al actualizar cliente"})


@app.delete("/api/clientes/{cliente_id}")
async def delete_cliente(cliente_id: int, username: str):
    """Elimina un cliente."""
    try:
        with get_db() as conn:
            # Obtener user_id
            user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if not user:
                raise HTTPException(status_code=404, detail={"message": "Usuario no encontrado"})
            
            # Verificar y eliminar
            result = conn.execute(
                "DELETE FROM clientes WHERE id = ? AND user_id = ?",
                (cliente_id, user["id"])
            )
            conn.commit()
            
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail={"message": "Cliente no encontrado"})
            
            return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar cliente: {e}")
        raise HTTPException(status_code=500, detail={"message": "Error al eliminar cliente"})


# ===============================================
# ENDPOINTS PARA OBRAS
# ===============================================

@app.get("/api/obras")
async def get_obras(username: str):
    """Obtiene todas las obras del usuario."""
    try:
        with get_db() as conn:
            # Obtener user_id
            user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if not user:
                raise HTTPException(status_code=404, detail={"message": "Usuario no encontrado"})
            
            # Obtener obras
            cursor = conn.execute(
                "SELECT id, nombre, ubicacion, estado, created_at FROM obras WHERE user_id = ? ORDER BY created_at DESC",
                (user["id"],)
            )
            obras = [dict(row) for row in cursor.fetchall()]
            return {"obras": obras}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener obras: {e}")
        raise HTTPException(status_code=500, detail={"message": "Error al obtener obras"})


@app.post("/api/obras")
async def create_obra(
    username: str = Form(...),
    nombre: str = Form(...),
    ubicacion: str = Form(None),
    estado: str = Form("activa")
):
    """Crea una nueva obra."""
    try:
        with get_db() as conn:
            # Obtener user_id
            user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if not user:
                raise HTTPException(status_code=404, detail={"message": "Usuario no encontrado"})
            
            # Insertar obra
            cursor = conn.execute(
                "INSERT INTO obras (user_id, nombre, ubicacion, estado) VALUES (?, ?, ?, ?)",
                (user["id"], nombre, ubicacion, estado)
            )
            conn.commit()
            
            return {"success": True, "id": cursor.lastrowid}
    except Exception as e:
        logger.error(f"Error al crear obra: {e}")
        raise HTTPException(status_code=500, detail={"message": "Error al crear obra"})


@app.put("/api/obras/{obra_id}")
async def update_obra(
    obra_id: int,
    username: str = Form(...),
    nombre: str = Form(...),
    ubicacion: str = Form(None),
    estado: str = Form("activa")
):
    """Actualiza una obra existente."""
    try:
        with get_db() as conn:
            # Obtener user_id
            user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if not user:
                raise HTTPException(status_code=404, detail={"message": "Usuario no encontrado"})
            
            # Verificar que la obra pertenece al usuario
            obra = conn.execute(
                "SELECT id FROM obras WHERE id = ? AND user_id = ?",
                (obra_id, user["id"])
            ).fetchone()
            
            if not obra:
                raise HTTPException(status_code=404, detail={"message": "Obra no encontrada"})
            
            # Actualizar obra
            conn.execute(
                "UPDATE obras SET nombre = ?, ubicacion = ?, estado = ? WHERE id = ?",
                (nombre, ubicacion, estado, obra_id)
            )
            conn.commit()
            
            return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar obra: {e}")
        raise HTTPException(status_code=500, detail={"message": "Error al actualizar obra"})


@app.delete("/api/obras/{obra_id}")
async def delete_obra(obra_id: int, username: str):
    """Elimina una obra."""
    try:
        with get_db() as conn:
            # Obtener user_id
            user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if not user:
                raise HTTPException(status_code=404, detail={"message": "Usuario no encontrado"})
            
            # Verificar y eliminar
            result = conn.execute(
                "DELETE FROM obras WHERE id = ? AND user_id = ?",
                (obra_id, user["id"])
            )
            conn.commit()
            
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail={"message": "Obra no encontrada"})
            
            return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar obra: {e}")
        raise HTTPException(status_code=500, detail={"message": "Error al eliminar obra"})


# ===============================================
# ENDPOINTS PARA PRODUCTOS
# ===============================================

@app.get("/api/productos")
async def get_productos(username: str):
    """Obtiene todos los productos del usuario."""
    try:
        with get_db() as conn:
            # Obtener user_id
            user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if not user:
                raise HTTPException(status_code=404, detail={"message": "Usuario no encontrado"})
            
            # Obtener productos
            cursor = conn.execute(
                "SELECT id, nombre, precio, created_at FROM productos WHERE user_id = ? ORDER BY created_at DESC",
                (user["id"],)
            )
            productos = [dict(row) for row in cursor.fetchall()]
            return {"productos": productos}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener productos: {e}")
        raise HTTPException(status_code=500, detail={"message": "Error al obtener productos"})


@app.post("/api/productos")
async def create_producto(
    username: str = Form(...),
    nombre: str = Form(...),
    precio: float = Form(0)
):
    """Crea un nuevo producto."""
    try:
        with get_db() as conn:
            # Obtener user_id
            user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if not user:
                raise HTTPException(status_code=404, detail={"message": "Usuario no encontrado"})
            
            # Insertar producto
            cursor = conn.execute(
                "INSERT INTO productos (user_id, nombre, precio) VALUES (?, ?, ?)",
                (user["id"], nombre, precio)
            )
            conn.commit()
            
            return {"success": True, "id": cursor.lastrowid}
    except Exception as e:
        logger.error(f"Error al crear producto: {e}")
        raise HTTPException(status_code=500, detail={"message": "Error al crear producto"})


@app.put("/api/productos/{producto_id}")
async def update_producto(
    producto_id: int,
    username: str = Form(...),
    nombre: str = Form(...),
    precio: float = Form(0)
):
    """Actualiza un producto existente."""
    try:
        with get_db() as conn:
            # Obtener user_id
            user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if not user:
                raise HTTPException(status_code=404, detail={"message": "Usuario no encontrado"})
            
            # Verificar que el producto pertenece al usuario
            producto = conn.execute(
                "SELECT id FROM productos WHERE id = ? AND user_id = ?",
                (producto_id, user["id"])
            ).fetchone()
            
            if not producto:
                raise HTTPException(status_code=404, detail={"message": "Producto no encontrado"})
            
            # Actualizar producto
            conn.execute(
                "UPDATE productos SET nombre = ?, precio = ? WHERE id = ?",
                (nombre, precio, producto_id)
            )
            conn.commit()
            
            return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar producto: {e}")
        raise HTTPException(status_code=500, detail={"message": "Error al actualizar producto"})


@app.delete("/api/productos/{producto_id}")
async def delete_producto(producto_id: int, username: str):
    """Elimina un producto."""
    try:
        with get_db() as conn:
            # Obtener user_id
            user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if not user:
                raise HTTPException(status_code=404, detail={"message": "Usuario no encontrado"})
            
            # Verificar y eliminar
            result = conn.execute(
                "DELETE FROM productos WHERE id = ? AND user_id = ?",
                (producto_id, user["id"])
            )
            conn.commit()
            
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail={"message": "Producto no encontrado"})
            
            return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar producto: {e}")
        raise HTTPException(status_code=500, detail={"message": "Error al eliminar producto"})


# ===============================================
# ENDPOINTS PARA REGISTROS
# ===============================================

@app.get("/api/registros")
async def get_registros(username: str, obra: str = None, fecha_inicio: str = None, fecha_fin: str = None):
    """Obtiene todos los registros del usuario con filtros opcionales."""
    try:
        with get_db() as conn:
            # Obtener user_id
            user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if not user:
                raise HTTPException(status_code=404, detail={"message": "Usuario no encontrado"})
            
            # Construir query con filtros
            query = "SELECT id, fecha, obra, totalCantidad, totalCobrar, totalPagado, status, clientesAdicionales, detalles, created_at FROM registros WHERE user_id = ?"
            params = [user["id"]]
            
            if obra:
                query += " AND obra = ?"
                params.append(obra)
            
            if fecha_inicio:
                query += " AND fecha >= ?"
                params.append(fecha_inicio)
            
            if fecha_fin:
                query += " AND fecha <= ?"
                params.append(fecha_fin)
            
            query += " ORDER BY fecha DESC, created_at DESC"
            
            # Obtener registros
            cursor = conn.execute(query, params)
            registros = [dict(row) for row in cursor.fetchall()]
            
            # Parsear JSON fields
            for registro in registros:
                if registro.get('clientesAdicionales'):
                    try:
                        import json
                        registro['clientesAdicionales'] = json.loads(registro['clientesAdicionales'])
                    except:
                        registro['clientesAdicionales'] = []
                else:
                    registro['clientesAdicionales'] = []
                    
                if registro.get('detalles'):
                    try:
                        import json
                        registro['detalles'] = json.loads(registro['detalles'])
                    except:
                        registro['detalles'] = []
                else:
                    registro['detalles'] = []
            
            return {"registros": registros}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener registros: {e}")
        raise HTTPException(status_code=500, detail={"message": "Error al obtener registros"})


@app.post("/api/registros")
async def create_registro(request: Request):
    """Crea un nuevo registro."""
    try:
        import json
        body = await request.json()
        
        username = body.get('username')
        fecha = body.get('fecha')
        obra = body.get('obra')
        totalCantidad = body.get('totalCantidad', 0)
        totalCobrar = body.get('totalCobrar', 0)
        totalPagado = body.get('totalPagado', 0)
        status = body.get('status', 'pendiente')
        clientesAdicionales = body.get('clientesAdicionales', [])
        detalles = body.get('detalles', [])
        
        with get_db() as conn:
            # Obtener user_id
            user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if not user:
                raise HTTPException(status_code=404, detail={"message": "Usuario no encontrado"})
            
            # Convertir listas a JSON
            clientesAdicionales_json = json.dumps(clientesAdicionales) if clientesAdicionales else None
            detalles_json = json.dumps(detalles) if detalles else None
            
            # Insertar registro
            cursor = conn.execute(
                """INSERT INTO registros 
                   (user_id, fecha, obra, totalCantidad, totalCobrar, totalPagado, status, clientesAdicionales, detalles) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user["id"], fecha, obra, totalCantidad, totalCobrar, totalPagado, status, 
                 clientesAdicionales_json, detalles_json)
            )
            conn.commit()
            
            return {"success": True, "id": cursor.lastrowid}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear registro: {e}")
        raise HTTPException(status_code=500, detail={"message": f"Error al crear registro: {str(e)}"})


@app.put("/api/registros/{registro_id}")
async def update_registro(registro_id: int, request: Request):
    """Actualiza un registro existente."""
    try:
        import json
        body = await request.json()
        
        username = body.get('username')
        fecha = body.get('fecha')
        obra = body.get('obra')
        totalCantidad = body.get('totalCantidad', 0)
        totalCobrar = body.get('totalCobrar', 0)
        totalPagado = body.get('totalPagado', 0)
        status = body.get('status', 'pendiente')
        clientesAdicionales = body.get('clientesAdicionales', [])
        detalles = body.get('detalles', [])
        
        with get_db() as conn:
            # Obtener user_id
            user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if not user:
                raise HTTPException(status_code=404, detail={"message": "Usuario no encontrado"})
            
            # Verificar que el registro pertenece al usuario
            registro = conn.execute(
                "SELECT id FROM registros WHERE id = ? AND user_id = ?",
                (registro_id, user["id"])
            ).fetchone()
            
            if not registro:
                raise HTTPException(status_code=404, detail={"message": "Registro no encontrado"})
            
            # Convertir listas a JSON
            clientesAdicionales_json = json.dumps(clientesAdicionales) if clientesAdicionales else None
            detalles_json = json.dumps(detalles) if detalles else None
            
            # Actualizar registro
            conn.execute(
                """UPDATE registros 
                   SET fecha = ?, obra = ?, totalCantidad = ?, totalCobrar = ?, 
                       totalPagado = ?, status = ?, clientesAdicionales = ?, detalles = ?
                   WHERE id = ?""",
                (fecha, obra, totalCantidad, totalCobrar, totalPagado, status, 
                 clientesAdicionales_json, detalles_json, registro_id)
            )
            conn.commit()
            
            return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar registro: {e}")
        raise HTTPException(status_code=500, detail={"message": f"Error al actualizar registro: {str(e)}"})


@app.delete("/api/registros/{registro_id}")
async def delete_registro(registro_id: int, username: str):
    """Elimina un registro."""
    try:
        with get_db() as conn:
            # Obtener user_id
            user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if not user:
                raise HTTPException(status_code=404, detail={"message": "Usuario no encontrado"})
            
            # Verificar y eliminar
            result = conn.execute(
                "DELETE FROM registros WHERE id = ? AND user_id = ?",
                (registro_id, user["id"])
            )
            conn.commit()
            
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail={"message": "Registro no encontrado"})
            
            return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar registro: {e}")
        raise HTTPException(status_code=500, detail={"message": "Error al eliminar registro"})


# ===============================================
# ENDPOINT PARA REPORTES/ESTADÍSTICAS
# ===============================================

@app.get("/api/reportes")
async def get_reportes(username: str, obra: str = None, fecha_inicio: str = None, fecha_fin: str = None):
    """Genera estadísticas y reportes basados en los registros."""
    try:
        with get_db() as conn:
            # Obtener user_id
            user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if not user:
                raise HTTPException(status_code=404, detail={"message": "Usuario no encontrado"})
            
            # Construir query con filtros
            query = "SELECT fecha, obra, totalCantidad, totalCobrar, totalPagado, status FROM registros WHERE user_id = ?"
            params = [user["id"]]
            
            if obra:
                query += " AND obra = ?"
                params.append(obra)
            
            if fecha_inicio:
                query += " AND fecha >= ?"
                params.append(fecha_inicio)
            
            if fecha_fin:
                query += " AND fecha <= ?"
                params.append(fecha_fin)
            
            query += " ORDER BY fecha DESC"
            
            # Obtener registros
            cursor = conn.execute(query, params)
            registros = [dict(row) for row in cursor.fetchall()]
            
            # Calcular estadísticas
            total_cobrar = sum(r['totalCobrar'] or 0 for r in registros)
            total_cobrado = sum(r['totalPagado'] or 0 for r in registros)
            total_pendiente = total_cobrar - total_cobrado
            total_cantidad = sum(r['totalCantidad'] or 0 for r in registros)
            
            # Agrupar por obra
            por_obra = {}
            for r in registros:
                obra_nombre = r['obra'] or 'Sin obra'
                if obra_nombre not in por_obra:
                    por_obra[obra_nombre] = {
                        'totalCobrar': 0,
                        'totalCobrado': 0,
                        'totalPendiente': 0,
                        'totalCantidad': 0
                    }
                por_obra[obra_nombre]['totalCobrar'] += r['totalCobrar'] or 0
                por_obra[obra_nombre]['totalCobrado'] += r['totalPagado'] or 0
                por_obra[obra_nombre]['totalPendiente'] += (r['totalCobrar'] or 0) - (r['totalPagado'] or 0)
                por_obra[obra_nombre]['totalCantidad'] += r['totalCantidad'] or 0
            
            # Agrupar por fecha
            por_fecha = {}
            for r in registros:
                fecha = r['fecha'] or 'Sin fecha'
                if fecha not in por_fecha:
                    por_fecha[fecha] = {
                        'totalCobrar': 0,
                        'totalCobrado': 0,
                        'totalPendiente': 0,
                        'totalCantidad': 0
                    }
                por_fecha[fecha]['totalCobrar'] += r['totalCobrar'] or 0
                por_fecha[fecha]['totalCobrado'] += r['totalPagado'] or 0
                por_fecha[fecha]['totalPendiente'] += (r['totalCobrar'] or 0) - (r['totalPagado'] or 0)
                por_fecha[fecha]['totalCantidad'] += r['totalCantidad'] or 0
            
            return {
                "totales": {
                    "totalCobrar": total_cobrar,
                    "totalCobrado": total_cobrado,
                    "totalPendiente": total_pendiente,
                    "totalCantidad": total_cantidad,
                    "totalRegistros": len(registros)
                },
                "porObra": por_obra,
                "porFecha": por_fecha,
                "registros": registros
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al generar reportes: {e}")
        raise HTTPException(status_code=500, detail={"message": "Error al generar reportes"})


if __name__ == "__main__":
    # Ejecuta la app para desarrollo. Requiere 'uvicorn' instalado.
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
