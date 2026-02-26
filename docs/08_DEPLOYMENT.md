# Deployment - Installazione e Produzione

## Opzioni di Deployment

FlaskERP può essere deployato in diversi modi a seconda delle tue esigenze.

### Docker (Consigliato)

Il metodo più semplice e supportato. Docker permette di avere un ambiente consistente tra sviluppo e produzione.

**Requisiti:**
- Docker
- Docker Compose
- PostgreSQL 14+

**Quick Start:**

```bash
# Clona il repository
git clone https://github.com/tuo-repo/flaskERP.git
cd flaskERP

# Avvia i container
docker compose up -d

# Esegui le migrazioni
docker compose exec backend flask db upgrade

# Accedi
# Frontend: http://localhost:5173
# Backend API: http://localhost:5000
```

### Deploy Manuale

Se preferisci non usare Docker:

**Backend:**
```bash
# Crea ambiente virtuale
python -m venv venv
source venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt

# Configura variabili
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:pass@localhost:5432/flaskerp

# Avvia
gunicorn -w 4 -b 0.0.0.0:5000 "backend:create_app()"
```

**Frontend:**
```bash
cd frontend
npm install
npm run build
# I file statici sono in dist/
```

---

## Configurazione Produzione

### Variabili Ambiente

| Variabile | Descrizione | Default |
|-----------|-------------|---------|
| FLASK_ENV | Ambiente | development |
| DATABASE_URL | Connection string DB | - |
| SECRET_KEY | Chiave per sessioni | - |
| JWT_SECRET_KEY | Chiave per JWT | - |

### Database

Usa PostgreSQL in produzione:

```sql
CREATE DATABASE flaskerp_prod;
CREATE USER flaskerp WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE flaskerp_prod TO flaskerp;
```

### Backend

Configura Gunicorn per produzione:

```bash
gunicorn \
  --workers 4 \
  --bind 0.0.0.0:5000 \
  --timeout 120 \
  --log-level info \
  "backend:create_app()"
```

### Frontend

Build per produzione:

```bash
cd frontend
npm run build
```

I file statici possono essere serviti da nginx o da un CDN.

---

## Nginx Configuration

Esempio configurazione nginx:

```nginx
server {
    listen 80;
    server_name tuodominio.it;

    # Frontend
    location / {
        root /var/www/flaskerp/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
 X-Real-IP        proxy_set_header $remote_addr;
    }
}
```

---

## SSL/HTTPS

In produzione usa sempre HTTPS.

### Certbot (Let's Encrypt)

```bash
# Installa certbot
apt install certbot python3-certbot-nginx

# Genera certificato
certbot --nginx -d tuodominio.it

# Rinnovo automatico
certbot renew --dry-run
```

---

## Monitoraggio e Logging

### Logging

Configura il logging per produzione:

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
```

### Health Check

Endpoint per health check:

```
GET /health
```

Ritorna 200 se l'applicazione è funzionante.

---

## Backup

### Database

Backup giornaliero automatico:

```bash
# Cron job
0 2 * * * pg_dump -U flaskerp flaskerp_prod > /backup/flaskerp_$(date +\%Y\%m\%d).sql
```

### Restore

```bash
psql -U flaskerp flaskerp_prod < backup/flaskerp_20260101.sql
```

---

## Scalabilità

### Orizzontale

Per scalare:

- Metti più instance di backend dietro un load balancer
- Usa Redis per sessioni condivise
- Database su server dedicato

### Cache

Abilita Redis per caching:

```python
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'RedisCache', 'CACHE_REDIS_URL': 'redis://localhost:6379/0'})
```

---

## Sicurezza Produzione

- Usa password forti per database
- Mantieni SECRET_KEY segreta
- Aggiorna regolarmente le dipendenze
- Monitora i log per attività sospette
- Usa firewall per limitare accessi

---

## Troubleshooting

### Il server non parte

- Controlla i log: `docker compose logs backend`
- Verifica le variabili ambiente
- Controlla la connessione al database

### Errori 500

- Consulta i log
- Verifica le autorizzazioni sul database
- Controlla la configurazione

### Performance

- Abilita caching
- Ottimizza le query
- Usa un database dedicato

---

*Documento aggiornato: Febbraio 2026*
