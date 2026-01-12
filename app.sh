#!/bin/bash
set -euo pipefail

if [ -f ".env" ]; then
    while IFS='=' read -r key value; do
        case "$key" in
            ""|\#*) continue ;;
        esac
        if [ -z "${!key+x}" ]; then
            export "$key=$value"
        fi
    done < .env
fi

APP_HOST="${APP_HOST:-127.0.0.1}"
APP_PORT="${APP_PORT:-8000}"
NGINX_SERVER_NAME="${NGINX_SERVER_NAME:-_}"
NGINX_SETUP="${NGINX_SETUP:-1}"
STOP_DB_ON_EXIT="${STOP_DB_ON_EXIT:-1}"
INSTALL_REQUIREMENTS="${INSTALL_REQUIREMENTS:-1}"
RUN_MIGRATIONS="${RUN_MIGRATIONS:-0}"

POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-fastapi-postgres}"
PG_USER="${PG_USER:-postgres}"
PG_PASSWORD="${PG_PASSWORD:-postgres}"
PG_DB="${PG_DB:-postgres}"
PG_PORT="${PG_PORT:-5432}"
POSTGRES_VOLUME="${POSTGRES_VOLUME:-fastapi-pgdata}"

if ! command -v docker >/dev/null 2>&1; then
    echo "Docker is required but not installed."
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    echo "Docker daemon is not running."
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is required but not installed."
    exit 1
fi

stop_db() {
    if [ "$STOP_DB_ON_EXIT" = "1" ]; then
        if docker ps --filter "name=^/${POSTGRES_CONTAINER}$" --format '{{.Names}}' | grep -xq "$POSTGRES_CONTAINER"; then
            docker stop "$POSTGRES_CONTAINER" >/dev/null
        fi
    fi
}

if [ "$STOP_DB_ON_EXIT" = "1" ]; then
    trap stop_db EXIT INT TERM
fi

get_mapped_port() {
    docker inspect -f '{{(index (index .NetworkSettings.Ports "5432/tcp") 0).HostPort}}' "$POSTGRES_CONTAINER" 2>/dev/null || true
}

if docker ps -a --filter "name=^/${POSTGRES_CONTAINER}$" --format '{{.Names}}' | grep -xq "$POSTGRES_CONTAINER"; then
    EXISTING_PORT="$(get_mapped_port)"
    if [ -n "$EXISTING_PORT" ] && [ "$EXISTING_PORT" != "$PG_PORT" ]; then
        echo "PostgreSQL container port mismatch (have ${EXISTING_PORT}, want ${PG_PORT}). Recreating..."
        docker rm -f "$POSTGRES_CONTAINER" >/dev/null
    else
        echo "PostgreSQL container exists, starting it..."
        docker start "$POSTGRES_CONTAINER" >/dev/null
    fi
fi

if ! docker ps -a --filter "name=^/${POSTGRES_CONTAINER}$" --format '{{.Names}}' | grep -xq "$POSTGRES_CONTAINER"; then
    echo "Creating PostgreSQL container..."
    docker volume create "$POSTGRES_VOLUME" >/dev/null
    docker run -d \
        --name "$POSTGRES_CONTAINER" \
        -e POSTGRES_USER="$PG_USER" \
        -e POSTGRES_PASSWORD="$PG_PASSWORD" \
        -e POSTGRES_DB="$PG_DB" \
        -p "$PG_PORT:5432" \
        -v "$POSTGRES_VOLUME:/var/lib/postgresql/data" \
        postgres:16
fi

echo "Waiting for PostgreSQL to start..."
for attempt in {1..30}; do
    if docker exec "$POSTGRES_CONTAINER" pg_isready -U "$PG_USER" -d "$PG_DB" >/dev/null 2>&1; then
        break
    fi
    sleep 1
done

if docker exec "$POSTGRES_CONTAINER" pg_isready -U "$PG_USER" -d "$PG_DB" >/dev/null 2>&1; then
    echo "✅ PostgreSQL is running on port ${PG_PORT}"
    echo "Connection string: postgresql://${PG_USER}:${PG_PASSWORD}@localhost:${PG_PORT}/${PG_DB}"
else
    echo "❌ Failed to start PostgreSQL"
    exit 1
fi

NGINX_CONF_PATH="/etc/nginx/sites-available/fastapi"
NGINX_LINK_PATH="/etc/nginx/sites-enabled/fastapi"

if [ "$NGINX_SETUP" = "1" ]; then
    if ! command -v nginx >/dev/null 2>&1; then
        echo "Nginx is required but not installed."
        exit 1
    fi

    if [ "$EUID" -ne 0 ] && ! command -v sudo >/dev/null 2>&1; then
        echo "sudo is required to configure Nginx (run as root or install sudo)."
        exit 1
    fi

    SUDO=""
    if [ "$EUID" -ne 0 ]; then
        SUDO="sudo"
    fi

$SUDO tee "$NGINX_CONF_PATH" >/dev/null <<NGINX
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

$SUDO ln -sf "$NGINX_CONF_PATH" "$NGINX_LINK_PATH"
$SUDO nginx -t
if command -v systemctl >/dev/null 2>&1; then
    $SUDO systemctl reload nginx
else
    $SUDO nginx -s reload
fi
fi

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

if [ -f "requirements.txt" ]; then
    if [ "$INSTALL_REQUIREMENTS" = "1" ]; then
        echo "Installing requirements..."
        pip install -r requirements.txt
    fi
fi

if [ "$RUN_MIGRATIONS" = "1" ]; then
    echo "Running database migrations..."
    PYTHONPATH=. alembic upgrade head
fi

exec uvicorn main:app --host "$APP_HOST" --port "$APP_PORT"
