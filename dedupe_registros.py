"""
Deduplicate registros in Render for 'Panchita\'s Catering'.
Keeps one per composite key (fecha, obra, totalCantidad, totalCobrar, totalPagado, status)
Prefers the earliest created_at; deletes the rest.
"""
import requests
import time
from collections import defaultdict

BASE = "https://aplicaci-n-mi.onrender.com"
USERNAME = "Panchita's Catering"

print("="*70)
print("DEDUPE REGISTROS - Panchita's Catering")
print("="*70)

# Fetch all registros
resp = requests.get(f"{BASE}/api/registros", params={"username": USERNAME}, timeout=30)
resp.raise_for_status()
payload = resp.json()
registros = payload.get("registros", [])
print(f"Total registros fetched: {len(registros)}")

# Group by composite key
buckets = defaultdict(list)
for r in registros:
    key = (
        r.get("fecha") or "",
        r.get("obra") or "",
        int(r.get("totalCantidad") or 0),
        float(r.get("totalCobrar") or 0.0),
        float(r.get("totalPagado") or 0.0),
        r.get("status") or "pendiente",
    )
    buckets[key].append(r)

# Decide deletions: keep one (earliest created_at), delete others
to_delete = []
for key, items in buckets.items():
    if len(items) <= 1:
        continue
    # sort by created_at ascending, then id ascending
    try:
        items_sorted = sorted(items, key=lambda x: (x.get("created_at") or "", x.get("id") or 0))
    except Exception:
        items_sorted = items
    keep = items_sorted[0]
    dels = items_sorted[1:]
    to_delete.extend(dels)

print(f"Duplicate buckets: {sum(1 for v in buckets.values() if len(v)>1)}")
print(f"Candidates to delete: {len(to_delete)}")

# Delete
deleted = 0
errors = 0
for d in to_delete:
    rid = d.get("id")
    if not rid:
        continue
    try:
        dr = requests.delete(f"{BASE}/api/registros/{rid}", params={"username": USERNAME}, timeout=30)
        if dr.status_code == 200:
            deleted += 1
            if deleted % 20 == 0:
                print(f"  Deleted {deleted} / {len(to_delete)}")
        else:
            errors += 1
            print(f"  ✗ Delete {rid} failed: {dr.status_code} {dr.text[:80]}")
    except Exception as e:
        errors += 1
        print(f"  ✗ Delete {rid} error: {e}")
    time.sleep(0.1)

print("\nSummary:")
print(f"Deleted: {deleted}")
print(f"Errors: {errors}")

# Verify
v = requests.get(f"{BASE}/api/reportes", params={"username": USERNAME}, timeout=30)
if v.status_code == 200:
    rep = v.json()
    print(f"TotalRegistros after: {rep.get('totales',{}).get('totalRegistros')}")
    print("Dates present:", list((rep.get('porFecha') or {}).keys()))
else:
    print("Verification failed:", v.status_code, v.text)
