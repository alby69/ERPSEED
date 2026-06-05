import requests, json

s = requests.Session()
r = s.post("http://localhost:5000/api/v1/auth/login", json={"email":"admin@erpseed.it","password":"admin123"})
tok = r.json().get("access_token")
s.headers.update({"Authorization": f"Bearer {tok}"})

# List models
r = s.get("http://localhost:5000/api/v1/sys-models")
print(f"Models: {r.status_code}")
if r.ok:
    data = r.json()
    if isinstance(data, dict): data = data.get("data", data.get("result", []))
    for m in data:
        print(f"  {m.get('name')} id={m.get('id')} table={m.get('tableName')} status={m.get('status')}")

# Get fields for vehicle (model id=1) via sys-fields
r = s.get("http://localhost:5000/api/v1/sys-fields")
print(f"\nAll fields: {r.status_code}")
if r.ok:
    data = r.json()
    if isinstance(data, dict): data = data.get("data", data.get("result", []))
    for f in data:
        mid = f.get("modelId") or f.get("model_id")
        print(f"  Field id={f.get('id')} name={f.get('name')} type={f.get('type')} modelId={mid}")

# Find brand field on vehicle (id=1)
brand_field = None
for f in data:
    mid = f.get("modelId") or f.get("model_id")
    if f.get("name") == "brand" and mid == 1:
        brand_field = f
        print(f"\nFound brand field: id={f['id']}")
        break

if brand_field:
    fid = brand_field["id"]
    r = s.delete(f"http://localhost:5000/api/v1/sys-fields/{fid}")
    print(f"Delete field {fid}: {r.status_code} {r.text[:300]}")
else:
    print("\nBrand field not found (may already be deleted)")
