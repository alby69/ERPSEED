FROM python:3.11-slim

WORKDIR /app

# Installa dipendenze di sistema per WeasyPrint
RUN apt-get update && apt-get install -y \
    build-essential libpango-1.0-0 libpangoft2-1.0-0 libjpeg62-turbo-dev libopenjp2-7-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia i requisiti e installa le dipendenze
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia il resto del codice sorgente
COPY . .

# Espone la porta e avvia l'app
CMD ["flask", "run", "--host=0.0.0.0"]