# FlaskERP - Deployment e Infrastruttura

## Setup Iniziale (Single Server)

### Configurazione Raccomandata

| Risorsa | Specifica | Costo |
|---------|-----------|-------|
| Server | Hetzner CPX4 | ~10€/mese |
| Database | PostgreSQL managed | ~5€/mese |
| Dominio | .com o .it | ~10€/anno |

### Docker Compose

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/flaskerp
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:14
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=flaskerp
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

volumes:
  pgdata:
```

---

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/flaskerp

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=your-secret-key
SECRET_KEY=your-secret-key

# Flask
FLASK_ENV=production
FLASK_DEBUG=0

# Mail
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=noreply@flaskerp.com
MAIL_PASSWORD=mail-password
```

---

## CI/CD con GitHub Actions

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker
        run: docker build -t flaskerp:${{ github.sha }} .
      
      - name: Run tests
        run: docker run flaskerp:${{ github.sha }} pytest
      
      - name: Deploy to server
        run: |
          ssh $SERVER "docker-compose pull"
          ssh $SERVER "docker-compose up -d"
```

---

## Backup e Recovery

### Backup Database

```bash
# Backup giornaliero
docker exec -t flaskerp_db_1 pg_dump -U user flaskerp > backup_$(date +%Y%m%d).sql

# Restore
docker exec -i flaskerp_db_1 psql -U user flaskerp < backup_20260220.sql
```

### Backup Automatici

| Tipo | Frequenza | Retention |
|------|-----------|-----------|
| Database | Giornaliero | 30 giorni |
| File uploads | Giornaliero | 7 giorni |
| Config | Settimanale | 12 settimane |

---

## Monitoring

### Uptime Monitoring
- Uptime Kuma (gratis)
- Prometheus + Grafana (avanzato)

### Log Aggregation
- Docker logs → stdout
- Integrazione con Sentry per errori

---

## Costo Stimato (Produzione)

| Voce | Mensile |
|------|---------|
| Server (VM) | 10€ |
| Database managed | 5€ |
| Dominio | 1€ |
| SSL (Let's Encrypt) | 0€ |
| **Totale** | **~16€/mese** |

---

*Documento aggiornato: Febbraio 2026*
