# FastAPI Docker Infrastructure

## Start

Create an environment file:

```bash
cp .env.example .env
```

Update secrets in `.env`, then run:

```bash
docker compose up --build -d
```

The API is available through nginx:

- `http://localhost/docs`

## Services

- `app` - FastAPI application on internal port `8000`
- `db` - PostgreSQL 16 with persistent `postgres_data` volume
- `nginx` - reverse proxy on `${NGINX_PORT:-80}`

## Operations

Run migrations manually:

```bash
docker compose exec app alembic upgrade head
```

View logs:

```bash
docker compose logs -f app
```

Stop services:

```bash
docker compose down
```
