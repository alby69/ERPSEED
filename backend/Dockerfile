FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    libcairo2-dev \
    libffi-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip

WORKDIR /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN mkdir -p /app/projects

ENV FLASK_APP=run.py
ENV FLASK_DEBUG=1
ENV PROJECT_TYPE=backend
ENV GIT_REPO_URL=https://github.com/alby69/ERPSEED.git
ENV GIT_BRANCH=erpseed/backend

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "run.py"]
