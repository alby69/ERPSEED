# ERPaaS - Infrastructure e Deployment

## Documento #08 - Infrastructure, Docker e CI/CD

---

## 1. Panoramica Infrastructure

### 1.1 Obiettivi

Progettare un'infrastruttura che:
- Supporti il modello di crescita graduale
- Sia gestibile da un team di 1-3 persone
- Costi meno di 100€/mese inizialmente
- Scala verso cloud completo quando necessario

### 1.2 Stack Infrastructure

| Componente | Scelta | Costo |
|------------|--------|-------|
| **Server** | Hetzner Cloud (CPX) | 5-20€/mese |
| **Database** | PostgreSQL managed | 10-15€/mese |
| **Cache** | Redis (stesso server) | incluso |
| **Storage** | S3/MinIO | 1-5€/mese |
| **DNS** | Cloudflare | gratis |
| **SSL** | Let's Encrypt | gratis |
| **Monitoring** | Uptime Kuma | gratis |
| **Totale** | | **~25-40€/mese** |

---

## 2. Architettura Deployment

### 2.1 Setup Iniziale (Single Server)

```
                    ┌─────────────────────────────────────────┐
                    │           INTERNET                       │
                    └──────────────────┬──────────────────────┘
                                       │
                                       ▼
                    ┌─────────────────────────────────────────┐
                    │         CLOUDFLARE (CDN + DNS)          │
                    │  • SSL Termination                     │
                    │  • DDoS Protection                     │
                    │  • Caching Static                      │
                    └──────────────────┬──────────────────────┘
                                       │
                                       ▼
                    ┌─────────────────────────────────────────┐
                    │    HETZNER CLOUD VM (CPX4 - 4CPU/8GB) │
                    │                                         │
                    │  ┌───────────────────────────────────┐  │
                    │  │        NGINX REVERSE PROXY       │  │
                    │  │   (SSL, Load Balancing)          │  │
                    │  └───────────────┬───────────────────┘  │
                    │                  │                      │
                    │      ┌───────────┼───────────┐          │
                    │      ▼           ▼           ▼          │
                    │  ┌───────┐  ┌───────┐  ┌───────┐      │
                    │  │ Flask │  │ Flask │  │ Flask │      │
                    │  │ App 1 │  │ App 2 │  │ App 3 │      │
                    │  └───────┘  └───────┘  └───────┘      │
                    │      │           │           │          │
                    │      └───────────┼───────────┘          │
                    │                  │                      │
                    │           ┌──────▼──────┐              │
                    │           │  PostgreSQL │              │
                    │           │   (Primary) │              │
                    │           └─────────────┘              │
                    │           ┌─────────────┐              │
                    │           │    Redis    │              │
                    │           │  (Cache/Q) │              │
                    │           └─────────────┘              │
                    │                                         │
                    └─────────────────────────────────────────┘
```

### 2.2 Setup Multi-Server (Futuro)

```
                    ┌─────────────────────────────────────────┐
                    │         CLOUDFLARE                      │
                    └──────────────────┬──────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────────┐
                    │     HETZNER LOAD BALANCER             │
                    └──────────────────┬──────────────────────┘
                                       │
         ┌──────────────────────────────┼──────────────────────┐
         │                              │                      │
         ▼                              ▼                      ▼
┌─────────────────┐          ┌─────────────────┐    ┌─────────────────┐
│   APP SERVER 1  │          │   APP SERVER 2  │    │   APP SERVER N  │
│   (Docker)     │          │   (Docker)      │    │   (Docker)      │
└────────┬────────┘          └────────┬────────┘    └────────┬────────┘
         │                            │                      │
         └────────────────────────────┼──────────────────────┘
                                      │
                    ┌──────────────────▼──────────────────────┐
                    │        HETZNER MANAGED DATABASE       │
                    │         (PostgreSQL + Replicas)        │
                    └───────────────────────────────────────┘
```

---

## 3. Docker Configuration

### 3.1 docker-compose.yml

```yaml
version: '3.8'

services:
  # Applicazione Flask
  app:
    build:
      context: .
      dockerfile: docker/Dockerfile
    container_name: flaskerp_app
    restart: unless-stopped
    environment:
      - FLASK_ENV=${FLASK_ENV:-production}
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET=${JWT_SECRET}
    volumes:
      - uploads:/app/uploads
      - ./logs:/app/logs
    depends_on:
      - db
      - redis
    networks:
      - flaskerp_network
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 1G

  # Database PostgreSQL
  db:
    image: postgres:15-alpine
    container_name: flaskerp_db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - flaskerp_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis per cache e task queue
  redis:
    image: redis:7-alpine
    container_name: flaskerp_redis
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - flaskerp_network
    command: redis-server --appendonly yes

  # Nginx come reverse proxy
  nginx:
    image: nginx:alpine
    container_name: flaskerp_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./docker/ssl:/etc/nginx/ssl:ro
      - static_files:/app/static:ro
    depends_on:
      - app
    networks:
      - flaskerp_network

  # Celery per task asincroni
  celery:
    build:
      context: .
      dockerfile: docker/Dockerfile
    container_name: flaskerp_celery
    command: celery -A app.celery worker -l info
    environment:
      - FLASK_ENV=${FLASK_ENV:-production}
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - uploads:/app/uploads
    depends_on:
      - db
      - redis
    networks:
      - flaskerp_network

  # Flower per monitoraggio Celery
  flower:
    build:
      context: .
      dockerfile: docker/Dockerfile
    container_name: flaskerp_flower
    command: celery -A app.celery flower --port=5555
    ports:
      - "5555:5555"
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
      - celery
    networks:
      - flaskerp_network

volumes:
  postgres_data:
  redis_data:
  uploads:
  static_files:

networks:
  flaskerp_network:
    driver: bridge
```

### 3.2 Dockerfile

```dockerfile
FROM python:3.11-slim

# Label
LABEL maintainer="FlaskERP Team"
LABEL description="FlaskERP - ERP as a Service Platform"

# Variabili d'ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directory lavoro
WORKDIR /app

# Installa dipendenze sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia codice applicazione
COPY . .

# Crea directory uploads
RUN mkdir -p /app/uploads /app/logs && \
    chmod -R 755 /app

# Utente non-root
RUN useradd --create-home appuser && \
    chown -R appuser:appuser /app
USER appuser

# Esporta porte
EXPOSE 8000

# Comando default
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "app:create_app()"]
```

### 3.3 nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript application/xml;

    # Upstream
    upstream flaskerp_app {
        least_conn;
        server app:8000 max_fails=3 fail_timeout=30s;
    }

    server {
        listen 80;
        server_name _;

        # Redirect to HTTPS (production)
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name _;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
        ssl_prefer_server_ciphers off;

        # Static files
        location /static/ {
            alias /app/static/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        # Uploads
        location /uploads/ {
            alias /app/uploads/;
            expires 7d;
        }

        # Proxy to Flask
        location / {
            proxy_pass http://flaskerp_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_redirect off;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # WebSocket support
        location /ws {
            proxy_pass http://flaskerp_app;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }
    }
}
```

---

## 4. Environment Variables

### 4.1 .env.example

```bash
# ===========================================
# FlaskERP Environment Configuration
# ===========================================

# Flask
FLASK_APP=app
FLASK_ENV=production  # development | production

# Security
SECRET_KEY=your-secret-key-min-32-chars-here-change-in-prod
JWT_SECRET=your-jwt-secret-min-32-chars

# Database
DB_HOST=db
DB_PORT=5432
DB_NAME=flaskerp
DB_USER=flaskerp
DB_PASSWORD=change-me-in-production

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# Email (SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Storage (S3)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET=flaskerp-uploads
AWS_S3_REGION=eu-central-1

# External Services
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
VIES_SOAP_ENDPOINT=

# Monitoring
SENTRY_DSN=
```

---

## 5. CI/CD Pipeline

### 5.1 GitHub Actions

File: `.github/workflows/deploy.yml`

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      
      - name: Run tests
        run: |
          pytest --cov=backend tests/
      
      - name: Lint
        run: |
          ruff check backend/

  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: docker/Dockerfile
          push: true
          tags: flaskerp/app:latest
          cache-from: type=registry,ref=flaskerp/app:buildcache
          cache-to: type=registry,ref=flaskerp/app:buildcache,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    
    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /opt/flaskerp
            docker-compose pull
            docker-compose up -d
            docker-compose exec -T app flask-cli db upgrade
            docker-compose exec -T celery celery purge
            docker system prune -f
```

### 5.2 GitHub Actions - PR

File: `.github/workflows/ci.yml`

```yaml
name: CI

on:
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: flaskerp_test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/flaskerp_test
          FLASK_ENV: testing
        run: |
          pytest tests/ -v --cov=backend --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

---

## 6. Backup e Recovery

### 6.1 Script Backup

```bash
#!/bin/bash
# scripts/backup.sh

set -e

# Config
BACKUP_DIR="/backups"
DB_NAME="${DB_NAME:-flaskerp}"
DB_USER="${DB_USER:-flaskerp}"
DATE=$(date +%Y%m%d_%H%M%S)

# Crea directory backup
mkdir -p $BACKUP_DIR

# Dump database
echo "Creating database backup..."
pg_dump -U $DB_USER -h db $DB_NAME > $BACKUP_DIR/db_$DATE.sql

# Comprimi
gzip $BACKUP_DIR/db_$DATE.sql

# Elimina backup più vecchi di 30 giorni
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete

echo "Backup completed: db_$DATE.sql.gz"
```

### 6.2 Cron Job

```bash
# /etc/cron.d/flaskerp-backup
# Backup giornaliero alle 2:00
0 2 * * * root /opt/flaskerp/scripts/backup.sh >> /var/log/flaskerp-backup.log 2>&1
```

---

## 7. Monitoring

### 7.1 Health Check

```python
# backend/core/api/health.py
from flask import Blueprint
from flask_jwt_extended import jwt_required
from ..services.tenant_context import TenantContext

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    """Health check endpoint."""
    return {
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    }

@health_bp.route('/health/ready')
def readiness_check():
    """Readiness check - verifica servizi."""
    checks = {
        'database': check_database(),
        'redis': check_redis(),
    }
    
    all_healthy = all(c['status'] == 'ok' for c in checks.values())
    
    return {
        'status': 'ready' if all_healthy else 'not_ready',
        'checks': checks
    }

def check_database():
    try:
        from backend.extensions import db
        db.session.execute('SELECT 1')
        return {'status': 'ok'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def check_redis():
    try:
        import redis
        r = redis.from_url(current_app.config['REDIS_URL'])
        r.ping()
        return {'status': 'ok'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
```

---

## 8. Checklist Deployment

### Pre-Deploy

- [ ] Repository configurato
- [ ] Secrets in GitHub Actions
- [ ] Dominio configurato (Cloudflare)
- [ ] Certificati SSL generati
- [ ] Backup automatici configurati
- [ ] Monitoring attivo (Uptime Kuma)

### Deploy

- [ ] Pull immagine/container
- [ ] Migration database eseguita
- [ ] Statici serviti
- [ ] SSL funzionante

### Post-Deploy

- [ ] Health check passa
- [ ] Login funziona
- [ ] CRUD base funziona
- [ ] Email inviate
- [ ] Logs accessibili

---

## 9. Scalabilità Progressiva

| Fase | Utenti | Tenant | Costo | Azioni |
|------|--------|--------|-------|--------|
| **1** | <100 | <10 | ~25€ | Single server |
| **2** | 100-500 | 10-50 | ~50€ | DB managed |
| **3** | 500-2000 | 50-200 | ~150€ | Load balancer |
| **4** | 2000+ | 200+ | ~500€ | Multi-region |

---

*Documento generato il 18 Febbraio 2026*
*Progetto: FlaskERP ERPaaS Platform*
*Documento #08 - Infrastructure e Deployment*
