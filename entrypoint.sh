#!/bin/sh
set -e

REPO_URL="${GIT_REPO_URL:-https://github.com/alby69/ERPSEED.git}"
BRANCH="${GIT_BRANCH:-main}"
PROJECT_TYPE="${PROJECT_TYPE:-backend}"

echo "Downloading branch: $BRANCH from $REPO_URL"

REPO_NAME=$(echo "$REPO_URL" | sed 's/.*github.com\///' | sed 's/\.git$//')
GITHUB_API_URL="https://api.github.com/repos/${REPO_NAME}/tarball/${BRANCH}"

echo "Downloading from: $GITHUB_API_URL"

mkdir -p /repo
cd /repo
curl -L -s "$GITHUB_API_URL" | tar xz

EXTRACTED_DIR=$(ls -d /repo/*/ 2>/dev/null | head -1)
if [ -n "$EXTRACTED_DIR" ]; then
    cp -r "$EXTRACTED_DIR"* /repo/
    rm -rf "$EXTRACTED_DIR"
fi

if [ "$PROJECT_TYPE" = "backend" ]; then
    cp -r /repo/* /app/
    if [ -f /app/requirements.txt ]; then
        pip install --no-cache-dir -r /app/requirements.txt
    fi
elif [ "$PROJECT_TYPE" = "frontend" ]; then
    if [ -d /repo/frontend ]; then
        cp -r /repo/frontend/* /app/
    else
        cp -r /repo/* /app/
    fi
fi

rm -rf /repo

cd /app
exec "$@"
