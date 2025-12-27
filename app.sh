#!/bin/bash
docker run -d \
       --name test-postgres \
       -e POSTGRES_PASSWORD=testpassword \
       -p 15432:5432 \
       postgres

source .venv/bin/activate
uvicorn main:app --reload    