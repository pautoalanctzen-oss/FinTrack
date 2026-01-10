import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple

import requests


# Default backend API base (override with env BACKEND_BASE_URL)
BASE_URL = os.environ.get("BACKEND_BASE_URL", "https://aplicaci-n-mi.onrender.com")


def _url(path: str) -> str:
    return f"{BASE_URL}{path}"


def _ts(s: str) -> float:
    try:
        # created_at is in SQLite default CURRENT_TIMESTAMP format
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").timestamp()
    except Exception:
        return 0.0


def get_clientes(username: str) -> List[Dict]:
    r = requests.get(_url("/api/clientes"), params={"username": username}, timeout=20)
    r.raise_for_status()
    return r.json().get("clientes", [])


def get_obras(username: str) -> List[Dict]:
    r = requests.get(_url("/api/obras"), params={"username": username}, timeout=20)
    r.raise_for_status()
    return r.json().get("obras", [])


def get_productos(username: str) -> List[Dict]:
    r = requests.get(_url("/api/productos"), params={"username": username}, timeout=20)
    r.raise_for_status()
    return r.json().get("productos", [])


def get_registros(username: str, fecha_inicio: str = None, fecha_fin: str = None) -> List[Dict]:
    params = {"username": username}
    if fecha_inicio:
        params["fecha_inicio"] = fecha_inicio
    if fecha_fin:
        params["fecha_fin"] = fecha_fin
    r = requests.get(_url("/api/registros"), params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("registros", [])


def delete_cliente(username: str, cliente_id: int) -> None:
    r = requests.delete(_url(f"/api/clientes/{cliente_id}"), params={"username": username}, timeout=20)
    r.raise_for_status()


def delete_obra(username: str, obra_id: int) -> None:
    r = requests.delete(_url(f"/api/obras/{obra_id}"), params={"username": username}, timeout=20)
    r.raise_for_status()


def delete_producto(username: str, producto_id: int) -> None:
    r = requests.delete(_url(f"/api/productos/{producto_id}"), params={"username": username}, timeout=20)
    r.raise_for_status()


def delete_registro(username: str, registro_id: int) -> None:
    r = requests.delete(_url(f"/api/registros/{registro_id}"), params={"username": username}, timeout=20)
    r.raise_for_status()


def dedupe_clientes(username: str, apply: bool) -> Dict:
    clientes = get_clientes(username)
    groups: Dict[Tuple[str, str, str], List[Dict]] = defaultdict(list)
    for c in clientes:
        key = (c.get("nombre", ""), c.get("obra", ""), c.get("cedula", ""))
        groups[key].append(c)

    to_delete: List[int] = []
    for key, items in groups.items():
        if len(items) <= 1:
            continue
        # Keep oldest (first created) to minimize breaking expectations
        items_sorted = sorted(items, key=lambda x: _ts(x.get("created_at", "")))
        keep = items_sorted[0]
        for dup in items_sorted[1:]:
            to_delete.append(dup["id"])
    if apply:
        for cid in to_delete:
            delete_cliente(username, cid)
    return {"total": len(clientes), "groups": len(groups), "deleted": len(to_delete)}


def dedupe_obras(username: str, apply: bool) -> Dict:
    obras = get_obras(username)
    groups: Dict[str, List[Dict]] = defaultdict(list)
    for o in obras:
        groups[o.get("nombre", "")].append(o)

    to_delete: List[int] = []
    for nombre, items in groups.items():
        if len(items) <= 1:
            continue
        items_sorted = sorted(items, key=lambda x: _ts(x.get("created_at", "")))
        keep = items_sorted[0]
        for dup in items_sorted[1:]:
            to_delete.append(dup["id"])
    if apply:
        for oid in to_delete:
            delete_obra(username, oid)
    return {"total": len(obras), "groups": len(groups), "deleted": len(to_delete)}


def dedupe_productos(username: str, apply: bool) -> Dict:
    productos = get_productos(username)
    groups: Dict[Tuple[str, float], List[Dict]] = defaultdict(list)
    for p in productos:
        key = (p.get("nombre", ""), float(p.get("precio", 0)))
        groups[key].append(p)

    to_delete: List[int] = []
    for key, items in groups.items():
        if len(items) <= 1:
            continue
        items_sorted = sorted(items, key=lambda x: _ts(x.get("created_at", "")))
        keep = items_sorted[0]
        for dup in items_sorted[1:]:
            to_delete.append(dup["id"])
    if apply:
        for pid in to_delete:
            delete_producto(username, pid)
    return {"total": len(productos), "groups": len(groups), "deleted": len(to_delete)}


def _reg_key(r: Dict) -> Tuple:
    # Prefer key without detalles to identify aggregates; when duplicates exist,
    # we will keep whichever has non-empty detalles.
    return (
        r.get("fecha", ""),
        r.get("obra", ""),
        int(r.get("totalCantidad", 0) or 0),
        float(r.get("totalCobrar", 0) or 0.0),
        float(r.get("totalPagado", 0) or 0.0),
        r.get("status", "pendiente"),
    )


def purge_all(username: str, apply: bool) -> Dict:
    """Elimina todos los clientes, obras, productos, y registros del usuario."""
    clientes = get_clientes(username)
    obras = get_obras(username)
    productos = get_productos(username)
    registros = get_registros(username)

    counts = {"clientes": 0, "obras": 0, "productos": 0, "registros": 0}

    if apply:
        # Delete in reverse order: registros first, then clientes/obras/productos
        for r in registros:
            try:
                delete_registro(username, r["id"])
                counts["registros"] += 1
            except Exception as e:
                print(f"Error deleting registro {r['id']}: {e}")

        for c in clientes:
            try:
                delete_cliente(username, c["id"])
                counts["clientes"] += 1
            except Exception as e:
                print(f"Error deleting cliente {c['id']}: {e}")

        for o in obras:
            try:
                delete_obra(username, o["id"])
                counts["obras"] += 1
            except Exception as e:
                print(f"Error deleting obra {o['id']}: {e}")

        for p in productos:
            try:
                delete_producto(username, p["id"])
                counts["productos"] += 1
            except Exception as e:
                print(f"Error deleting producto {p['id']}: {e}")
    else:
        counts = {"clientes": len(clientes), "obras": len(obras), "productos": len(productos), "registros": len(registros)}

    return counts


def dedupe_registros(username: str, apply: bool, fecha_inicio: str = None, fecha_fin: str = None) -> Dict:
    registros = get_registros(username, fecha_inicio, fecha_fin)
    groups: Dict[Tuple, List[Dict]] = defaultdict(list)
    for r in registros:
        groups[_reg_key(r)].append(r)

    to_delete: List[int] = []
    for key, items in groups.items():
        if len(items) <= 1:
            continue
        # Prefer record with non-empty detalles; otherwise keep oldest
        with_detalles = [i for i in items if (i.get("detalles") or [])]
        if with_detalles:
            keep = sorted(with_detalles, key=lambda x: _ts(x.get("created_at", "")))[0]
        else:
            keep = sorted(items, key=lambda x: _ts(x.get("created_at", "")))[0]
        for dup in items:
            if dup["id"] != keep["id"]:
                to_delete.append(dup["id"])
    if apply:
        for rid in to_delete:
            delete_registro(username, rid)
    return {"total": len(registros), "groups": len(groups), "deleted": len(to_delete)}


def import_registros_from_backup(username: str, path: str, apply: bool) -> Dict:
    """Importa clientes, obras, productos y registros desde un backup JSON.
    Espera un objeto con claves 'clientes', 'obras', 'productos', 'registros'.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    clientes = data.get("clientes", [])
    obras = data.get("obras", [])
    productos = data.get("productos", [])
    registros = data.get("registros", [])
    
    counts = {"clientes": 0, "obras": 0, "productos": 0, "registros": 0}
    
    if apply:
        # Import clientes
        for c in clientes:
            try:
                payload = {
                    "username": username,
                    "nombre": c.get("nombre", ""),
                    "cedula": c.get("cedula"),
                    "obra": c.get("obra"),
                    "estado": c.get("estado", "activo"),
                    "fecha": c.get("fecha"),
                }
                r = requests.post(_url("/api/clientes"), data=payload, timeout=30)
                r.raise_for_status()
                if r.json().get("success"):
                    counts["clientes"] += 1
            except Exception as e:
                print(f"Error importing cliente {c.get('nombre')}: {e}")
        
        # Import obras
        for o in obras:
            try:
                payload = {
                    "username": username,
                    "nombre": o.get("nombre", ""),
                    "ubicacion": o.get("ubicacion"),
                    "estado": o.get("estado", "activa"),
                }
                r = requests.post(_url("/api/obras"), data=payload, timeout=30)
                r.raise_for_status()
                if r.json().get("success"):
                    counts["obras"] += 1
            except Exception as e:
                print(f"Error importing obra {o.get('nombre')}: {e}")
        
        # Import productos
        for p in productos:
            try:
                payload = {
                    "username": username,
                    "nombre": p.get("nombre", ""),
                    "precio": float(p.get("precio", 0)),
                }
                r = requests.post(_url("/api/productos"), data=payload, timeout=30)
                r.raise_for_status()
                if r.json().get("success"):
                    counts["productos"] += 1
            except Exception as e:
                print(f"Error importing producto {p.get('nombre')}: {e}")
        
        # Import registros
        for rec in registros:
            try:
                payload = {
                    "username": username,
                    "fecha": rec.get("fecha") or rec.get("dia") or rec.get("fechaRegistro"),
                    "obra": rec.get("obra"),
                    "totalCantidad": rec.get("totalCantidad", 0),
                    "totalCobrar": rec.get("totalCobrar", 0),
                    "totalPagado": rec.get("totalPagado", 0),
                    "status": rec.get("status", "pendiente"),
                    # Map 'items' to 'detalles'
                    "detalles": rec.get("items") or rec.get("detalles") or [],
                }
                # Derivar clientesAdicionales si existen en items
                adicionales = []
                for it in payload["detalles"]:
                    if str(it.get("tipo", "")).lower() == "adicional":
                        adicionales.append({"cliente": it.get("cliente"), "valor": it.get("costo", it.get("precio", 0))})
                if adicionales:
                    payload["clientesAdicionales"] = adicionales
                r = requests.post(_url("/api/registros"), json=payload, timeout=30)
                r.raise_for_status()
                if r.json().get("success"):
                    counts["registros"] += 1
            except Exception as e:
                print(f"Error importing registro {rec.get('fecha')}: {e}")
    
    return {"imported": counts, "total_in_file": {"clientes": len(clientes), "obras": len(obras), "productos": len(productos), "registros": len(registros)}}



def main():
    parser = argparse.ArgumentParser(description="Maintenance tools: dedupe and import")
    parser.add_argument("--username", required=True, help="Target username (e.g., Panchita's Catering)")
    parser.add_argument("--action", required=True, choices=[
        "dry-run", "export-all", "purge-all", "dedupe-all", "dedupe-clientes", "dedupe-obras", "dedupe-productos", "dedupe-registros", "import-backup"
    ])
    parser.add_argument("--backup", help="Path to backup JSON for import-backup/export-all")
    parser.add_argument("--fecha_inicio", help="Start date for registros dedupe YYYY-MM-DD")
    parser.add_argument("--fecha_fin", help="End date for registros dedupe YYYY-MM-DD")
    parser.add_argument("--apply", action="store_true", help="Apply changes; otherwise just report")
    args = parser.parse_args()

    username = args.username

    if args.action == "dry-run":
        print("Backend:", BASE_URL)
        print("Clientes:", len(get_clientes(username)))
        print("Obras:", len(get_obras(username)))
        print("Productos:", len(get_productos(username)))
        regs = get_registros(username, args.fecha_inicio, args.fecha_fin)
        print("Registros:", len(regs))
        return

    if args.action == "export-all":
        out_path = args.backup or f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        pkg = {
            "clientes": get_clientes(username),
            "obras": get_obras(username),
            "productos": get_productos(username),
            "registros": get_registros(username, args.fecha_inicio, args.fecha_fin),
            "meta": {"backend": BASE_URL, "username": username, "fecha_inicio": args.fecha_inicio, "fecha_fin": args.fecha_fin}
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(pkg, f, ensure_ascii=False, indent=2)
        print("Exported:", out_path)
        return

    if args.action == "purge-all":
        res = purge_all(username, apply=args.apply)
        print("Purged:", res)
        return

        res = dedupe_clientes(username, apply=args.apply)
        print("Clientes:", res)
        if args.action == "dedupe-clientes":
            return

    if args.action in ("dedupe-obras", "dedupe-all"):
        res = dedupe_obras(username, apply=args.apply)
        print("Obras:", res)
        if args.action == "dedupe-obras":
            return

    if args.action in ("dedupe-productos", "dedupe-all"):
        res = dedupe_productos(username, apply=args.apply)
        print("Productos:", res)
        if args.action == "dedupe-productos":
            return

    if args.action in ("dedupe-registros", "dedupe-all"):
        res = dedupe_registros(username, apply=args.apply, fecha_inicio=args.fecha_inicio, fecha_fin=args.fecha_fin)
        print("Registros:", res)
        return

    if args.action == "import-backup":
        if not args.backup:
            print("--backup path is required")
            sys.exit(2)
        res = import_registros_from_backup(username, args.backup, apply=args.apply)
        print("Import:", res)
        return


if __name__ == "__main__":
    main()
