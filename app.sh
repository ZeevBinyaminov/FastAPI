#!/bin/bash
set -euo pipefail

if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

APP_HOST="${APP_HOST:-127.0.0.1}"
APP_PORT="${APP_PORT:-8000}"
NGINX_SERVER_NAME="${NGINX_SERVER_NAME:-_}"
NGINX_SETUP="${NGINX_SETUP:-1}"

POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-fastapi-postgres}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_VOLUME="${POSTGRES_VOLUME:-fastapi-pgdata}"

if ! command -v docker >/dev/null 2>&1; then
    echo "Docker is required but not installed."
    exit 1
fi

if ! command -v nginx >/dev/null 2>&1; then
    echo "Nginx is required but not installed."
    exit 1
fi

stop_db() {
    if docker container ls | grep -q "$POSTGRES_CONTAINER"; then
        docker stop "$POSTGRES_CONTAINER" >/dev/null
    fi
}

trap stop_db EXIT INT TERM

if docker container ls -a | grep -q "$POSTGRES_CONTAINER"; then
    echo "PostgreSQL container exists, starting it..."
    docker start "$POSTGRES_CONTAINER" >/dev/null
else
    echo "Creating PostgreSQL container..."
    docker volume create "$POSTGRES_VOLUME" >/dev/null
    docker run -d \
        --name "$POSTGRES_CONTAINER" \
        -e POSTGRES_USER="$POSTGRES_USER" \
        -e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
        -e POSTGRES_DB="$POSTGRES_DB" \
        -p "$POSTGRES_PORT:5432" \
        -v "$POSTGRES_VOLUME:/var/lib/postgresql/data" \
        postgres:16
fi

echo "Waiting for PostgreSQL to start..."
sleep 3

if docker container ls | grep -q "$POSTGRES_CONTAINER"; then
    echo "✅ PostgreSQL is running on port ${POSTGRES_PORT}"
    echo "Connection string: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:${POSTGRES_PORT}/${POSTGRES_DB}"
else
    echo "❌ Failed to start PostgreSQL"
    exit 1
fi

NGINX_CONF_PATH="/etc/nginx/sites-available/fastapi"
NGINX_LINK_PATH="/etc/nginx/sites-enabled/fastapi"

if [ "$NGINX_SETUP" = "1" ]; then
sudo tee "$NGINX_CONF_PATH" >/dev/null <<NGINX
server {
    listen 80;
    server_name ${NGINX_SERVER_NAME};

    location / {
        proxy_pass http://${APP_HOST}:${APP_PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
NGINX

sudo ln -sf "$NGINX_CONF_PATH" "$NGINX_LINK_PATH"
sudo nginx -t
sudo systemctl reload nginx
fi

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

source .venv/bin/activate

if [ -f "requirements.txt" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
fi

exec uvicorn main:app --host "$APP_HOST" --port "$APP_PORT"
