"""
Import registros from a localStorage backup JSON into Render.
Requires a JSON file exported via frontend/export_localstorage.html or RECUPERAR_DATOS.html.
Maps `items` to backend `detalles` to preserve editability.
"""
import json
import sys
import time
import requests

BASE = "https://aplicaci-n-mi.onrender.com"
USERNAME = "Panchita's Catering"

if len(sys.argv) < 2:
    print("Usage: import_registros_from_backup.py <backup_json_path>")
    sys.exit(1)

path = sys.argv[1]
print("="*70)
print("IMPORT REGISTROS FROM BACKUP")
print("="*70)
print("File:", path)

with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

registros = data.get('registros') or data
if not isinstance(registros, list):
    print("Backup JSON does not contain a 'registros' array. Aborting.")
    sys.exit(1)

print(f"Registros to import: {len(registros)}")

# Optional: delete existing registros (confirm)
resp = requests.get(f"{BASE}/api/registros", params={"username": USERNAME}, timeout=30)
existing = resp.json().get('registros', [])
print(f"Existing registros in backend: {len(existing)}")

confirm = input("Delete ALL existing registros for this user before import? (y/N): ").strip().lower()
if confirm == 'y':
    deleted = 0
    for r in existing:
        rid = r.get('id')
        if not rid:
            continue
        dr = requests.delete(f"{BASE}/api/registros/{rid}", params={"username": USERNAME}, timeout=30)
        if dr.status_code == 200:
            deleted += 1
        time.sleep(0.05)
    print(f"Deleted {deleted} registros.")

# Import
created = 0
errors = 0
for r in registros:
    payload = {
        "username": USERNAME,
        "fecha": r.get("fecha"),
        "obra": r.get("obra"),
        "totalCantidad": int(r.get("totalCantidad") or 0),
        "totalCobrar": float(r.get("totalCobrar") or 0.0),
        "totalPagado": float(r.get("totalPagado") or 0.0),
        "status": r.get("status") or "pendiente",
        # Preserve original items into detalles for editability
        "detalles": r.get("items") or r.get("detalles") or []
    }
    # For adicionales, capture names list if present
    if (r.get("tipo") == 'adicional') and payload["detalles"]:
        payload["clientesAdicionales"] = [it.get("clienteNombre") for it in payload["detalles"] if it.get("clienteNombre")]
    try:
        pr = requests.post(f"{BASE}/api/registros", json=payload, timeout=30)
        if pr.status_code == 200:
            created += 1
        else:
            errors += 1
            print(f"  ✗ {pr.status_code} {pr.text[:100]}")
    except Exception as e:
        errors += 1
        print(f"  ✗ Error: {e}")
    time.sleep(0.1)

print("\nSummary:")
print(f"Created: {created}")
print(f"Errors: {errors}")

vr = requests.get(f"{BASE}/api/reportes", params={"username": USERNAME}, timeout=30)
if vr.status_code == 200:
    rep = vr.json()
    print(f"TotalRegistros after import: {rep.get('totales',{}).get('totalRegistros')}")
    print("Dates:", sorted(list((rep.get('porFecha') or {}).keys())))
else:
    print("Verification failed:", vr.status_code, vr.text)
