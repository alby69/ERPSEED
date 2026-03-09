# Fase 1: Build - Installa le dipendenze di sistema per pycairo
FROM python:3.12-slim AS builder

WORKDIR /app

# Installa le dipendenze di build e runtime per pycairo (richiesto da xhtml2pdf)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2-dev \
    libffi-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Installa le dipendenze Python
RUN pip install --upgrade pip

# Copia il file delle dipendenze e crea i "wheels" (pacchetti pre-compilati)
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt

# Fase 2: Immagine finale - Leggera e pronta per l'esecuzione
FROM python:3.12-slim

WORKDIR /app

# Installa le dipendenze di runtime per pycairo
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libffi8 \
    && rm -rf /var/lib/apt/lists/*

# Copia le dipendenze pre-compilate dalla fase di build e installale
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Copia il codice dell'applicazione (verrà sovrascritto dal volume in dev)
COPY ./backend ./backend

# Imposta la variabile d'ambiente per Flask e per i log
ENV FLASK_APP=backend
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 5000