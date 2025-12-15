from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from datetime import date
import sqlite3
import bcrypt
from contextlib import contextmanager
import os
import re


app = FastAPI()

# Base de datos SQLite (ruta absoluta para evitar inconsistencias por CWD)
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


@contextmanager
def get_db():
    """Context manager para manejar conexiones a la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Inicializa la base de datos con la tabla de usuarios."""
    with get_db() as conn:
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
        conn.commit()


# Inicializar DB al arrancar
init_db()


def ensure_demo_user():
    """Crea un usuario de prueba si no existe para facilitar el acceso.

    Usuario: demo
    Contraseña: Demo1234
    """
    email = "demo@example.com"
    username = "demo"
    birthdate = "2000-01-01"
    password_plain = "Demo1234"
    with get_db() as conn:
        cur = conn.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
        row = cur.fetchone()
        if row:
            return
        password_hash = bcrypt.hashpw(password_plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        conn.execute(
            "INSERT INTO users (email, username, birthdate, password_hash) VALUES (?, ?, ?, ?)",
            (email, username, birthdate, password_hash),
        )
        conn.commit()


# Asegurar usuario demo persistente
ensure_demo_user()

# Montar archivos estáticos del frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Directorio de plantillas (para compatibilidad, aunque ahora usamos archivos estáticos)
templates = Jinja2Templates(directory="templates")

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
    return {"status": "ok"}


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
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        
        if not row:
            return {"username": username, "authenticated": False, "message": "Credenciales inválidas"}
        
        # Verificar contraseña con bcrypt
        password_hash = row["password_hash"]
        if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            return {"username": username, "authenticated": True, "message": "Autenticado correctamente"}
        else:
            return {"username": username, "authenticated": False, "message": "Credenciales inválidas"}


@app.post("/api/register")
async def api_register(
    email: str = Form(...),
    username: str = Form(...),
    birthdate: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    """Registro: valida campos, crea usuario en DB con contraseña hasheada."""
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
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail={"message": "El usuario o correo ya existe"})

    return {"success": True, "message": "Registro exitoso"}


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


if __name__ == "__main__":
    # Ejecuta la app para desarrollo. Requiere 'uvicorn' instalado.
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
