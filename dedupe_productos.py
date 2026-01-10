"""
Deduplicate productos for 'Panchita\'s Catering' in Render.
Groups by (nombre, precio) and keeps the earliest; deletes duplicates.
"""
import requests
import time
from collections import defaultdict

BASE = "https://aplicaci-n-mi.onrender.com"
USERNAME = "Panchita's Catering"

print("="*70)
print("DEDUPE PRODUCTOS - Panchita's Catering")
print("="*70)

# Fetch all productos
resp = requests.get(f"{BASE}/api/productos", params={"username": USERNAME}, timeout=30)
resp.raise_for_status()
payload = resp.json()
productos = payload.get("productos", [])
print(f"Total productos fetched: {len(productos)}")

buckets = defaultdict(list)
for p in productos:
    key = (p.get("nombre",""), float(p.get("precio") or 0.0))
    buckets[key].append(p)

# Prepare deletions
to_delete = []
for key, items in buckets.items():
    if len(items) <= 1:
        continue
    try:
        items_sorted = sorted(items, key=lambda x: (x.get("created_at") or "", x.get("id") or 0))
    except Exception:
        items_sorted = items
    keep = items_sorted[0]
    dels = items_sorted[1:]
    to_delete.extend(dels)

print(f"Duplicate groups: {sum(1 for v in buckets.values() if len(v)>1)}")
print(f"Candidates to delete: {len(to_delete)}")

# Delete duplicates
deleted = 0
errors = 0
for d in to_delete:
    pid = d.get("id")
    if not pid:
        continue
    try:
        dr = requests.delete(f"{BASE}/api/productos/{pid}", params={"username": USERNAME}, timeout=30)
        if dr.status_code == 200:
            deleted += 1
            if deleted % 10 == 0:
                print(f"  Deleted {deleted}/{len(to_delete)}")
        else:
            errors += 1
            print(f"  ✗ Delete {pid} failed: {dr.status_code} {dr.text[:80]}")
    except Exception as e:
        errors += 1
        print(f"  ✗ Delete {pid} error: {e}")
    time.sleep(0.1)

print("\nSummary:")
print(f"Deleted: {deleted}")
print(f"Errors: {errors}")

# Verify
v = requests.get(f"{BASE}/api/productos", params={"username": USERNAME}, timeout=30)
if v.status_code == 200:
    final = v.json().get("productos", [])
    print(f"Productos after: {len(final)}")
    print("List:", [(p.get("nombre"), p.get("precio")) for p in final])
else:
    print("Verification failed:", v.status_code, v.text)
