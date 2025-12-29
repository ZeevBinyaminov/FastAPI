#!/bin/bash
set -euo pipefail

if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

# Check if test-postgres container exists (running or stopped)
if docker container ls -a | grep -q test-postgres; then
    echo "Container exists, starting it..."
    docker start test-postgres
else
    echo "Container doesn't exist, creating new one..."
    docker run -d \
        --name test-postgres \
        -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-testpassword} \
        -p ${POSTGRES_PORT:-15432}:5432 \
        postgres
fi

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to start..."
sleep 3

# Check if it's running
if docker container ls | grep -q test-postgres; then
    echo "✅ PostgreSQL is running on port ${POSTGRES_PORT:-15432}"
    echo "Connection string: postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-testpassword}@localhost:${POSTGRES_PORT:-15432}/${POSTGRES_DB:-postgres}"
else
    echo "❌ Failed to start PostgreSQL"
    exit 1
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

uvicorn main:app --reload
