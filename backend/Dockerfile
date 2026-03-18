FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a folder for templates/projects
RUN mkdir -p /app/projects

COPY . .

ENV FLASK_APP=run.py
ENV FLASK_DEBUG=1

CMD ["python", "run.py"]