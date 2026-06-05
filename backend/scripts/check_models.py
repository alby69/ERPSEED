import requests, json, sys

s = requests.Session()
r = s.post("http://localhost:5000/api/v1/auth/login", json={"email":"admin@erpseed.it","password":"admin123"})
tok = r.json().get("access_token")
s.headers.update({"Authorization": f"Bearer {tok}"})

r = s.get("http://localhost:5000/api/v1/projects/1/models")
data = r.json()
if isinstance(data, dict): data = data.get("result", data)
for m in data:
    print(f"Model: {m.get('name')} (id={m.get('id')}, table={m.get('tableName')}, status={m.get('status')})")
    r2 = s.get(f"http://localhost:5000/api/v1/projects/1/models/{m['id']}/fields")
    fdata = r2.json()
    if isinstance(fdata, dict): fdata = fdata.get("result", fdata)
    for f in fdata:
        print(f"  Field: {f.get('name')} type={f.get('type')} required={f.get('required')}")
