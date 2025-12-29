#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/root/DeFiProject/FastAPI"
APP_USER="root"
APP_PORT="8000"
DOMAIN_OR_IP="185.200.176.219"

# Postgres config
PG_USER="postgres"
PG_PASSWORD="postgres"
PG_DB="postgres"
PG_PORT="5432"

# 1) Install system dependencies
apt update
apt install -y git python3-venv python3-pip nginx docker.io docker-compose-plugin
usermod -aG docker "$APP_USER" || true

# 2) Postgres in Docker
docker volume create pgdata >/dev/null 2>&1 || true
docker rm -f postgres >/dev/null 2>&1 || true
docker run -d --name postgres \
  -e POSTGRES_USER="$PG_USER" \
  -e POSTGRES_PASSWORD="$PG_PASSWORD" \
  -e POSTGRES_DB="$PG_DB" \
  -p "$PG_PORT:5432" \
  -v pgdata:/var/lib/postgresql/data \
  postgres:16

# 3) Python env + deps
cd "$APP_DIR"
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

# 4) .env
cat > .env <<ENV
POSTGRES_HOST=localhost
POSTGRES_PORT=$PG_PORT
POSTGRES_USER=$PG_USER
POSTGRES_PASSWORD=$PG_PASSWORD
POSTGRES_DB=$PG_DB
JWT_SECRET_KEY=change_me
JWT_ALGORITHM=HS256
JWT_EXPIRES_MINUTES=60
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin
ENV

# 5) Migrations
PYTHONPATH=. alembic upgrade head

# 6) systemd unit
cat >/etc/systemd/system/fastapi.service <<SERVICE
[Unit]
Description=FastAPI app
After=network.target

[Service]
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PYTHONPATH=$APP_DIR"
ExecStart=$APP_DIR/.venv/bin/uvicorn main:app --host 127.0.0.1 --port $APP_PORT
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable fastapi
systemctl restart fastapi

# 7) Nginx config
cat >/etc/nginx/sites-available/fastapi <<NGINX
server {
    listen 80;
    server_name $DOMAIN_OR_IP;

    location / {
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled/fastapi
nginx -t
systemctl restart nginx

echo "DONE. Check: http://$DOMAIN_OR_IP/docs"
