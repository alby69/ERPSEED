import requests, json

s = requests.Session()
r = s.post("http://localhost:5000/api/v1/auth/login", json={"email":"admin@erpseed.it","password":"admin123"})
tok = r.json().get("access_token")
s.headers.update({"Authorization": f"Bearer {tok}"})

# Test with project_id (snake_case) - what frontend sends
r = s.post("http://localhost:5000/api/v1/ai/generations",
          json={"request":"Crea un modello Foo", "project_id": 1},
          timeout=60)
print(f"project_id (snake): {r.status_code}")
print(r.text[:500])

print()

# Test with projectId (camelCase) - what schema expects
r = s.post("http://localhost:5000/api/v1/ai/generations",
          json={"request":"Crea un modello Foo", "projectId": 1},
          timeout=60)
print(f"projectId (camel): {r.status_code}")
print(r.text[:500])

print()

# Test conversations endpoint
r = s.get("http://localhost:5000/api/v1/ai/conversations?projectId=1", timeout=30)
print(f"conversations: {r.status_code}")
print(r.text[:500])
