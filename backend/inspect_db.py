import os
import json
import sqlite3
from contextlib import closing

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


def connect():
    return sqlite3.connect(DB_PATH)


def print_schema():
    with closing(connect()) as conn:
        cur = conn.execute("SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name;")
        rows = cur.fetchall()
        if not rows:
            print("No hay tablas en la base de datos.")
            return
        print("\nEsquema de la base de datos:")
        for name, sql in rows:
            print(f"\n-- Tabla: {name}\n{sql}\n")


def list_users(limit=50):
    with closing(connect()) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT id, email, username, birthdate, created_at FROM users ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = [dict(r) for r in cur.fetchall()]
        if not rows:
            print("No hay usuarios registrados.")
        else:
            print(f"\nUsuarios (máx {limit}):")
            for r in rows:
                print(f"- #{r['id']} {r['username']} <{r['email']}> | nacimiento={r['birthdate']} | creado={r['created_at']}")
        return rows


def export_json(path="users_export.json"):
    rows = list_users(limit=100000) or []
    out_path = os.path.join(os.path.dirname(__file__), path)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"\nExportado a {out_path} ({len(rows)} usuarios)")


if __name__ == "__main__":
    print(f"Base de datos: {DB_PATH}\n")
    print_schema()
    list_users()
    # Para exportar a JSON legible, ejecuta: python inspect_db.py > vista rápida
    # O descomenta la línea siguiente:
    # export_json()
