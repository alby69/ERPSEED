import requests, json

s = requests.Session()
r = s.post("http://localhost:5000/api/v1/auth/login", json={"email":"admin@erpseed.it","password":"admin123"})
tok = r.json().get("access_token")
s.headers.update({"Authorization": f"Bearer {tok}"})

prompt = """Crea un modello Brand per le marche automobilistiche, con i seguenti campi:
- name (stringa, obbligatorio, unico): nome della marca (es. Fiat, Ford, Tesla, BMW, Mercedes, Toyota, Volkswagen)
- country (stringa, opzionale): paese d'origine

Poi, crea una configurazione per modificare il modello Vehicle esistente:
1. Aggiungi un nuovo campo brand_id di tipo "relation" al modello Vehicle, che punti alla tabella "brand" con label_field "name"
2. Il vecchio campo "brand" di tipo select su Vehicle va rimosso (non incluso nella configurazione finale)"""

r = s.post("http://localhost:5000/api/v1/ai/generations",
          json={"request": prompt, "projectId": 1},
          timeout=60)
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2)[:2000])
