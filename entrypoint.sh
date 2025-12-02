#!/bin/bash

while ! pg_isready -h $POSTGRES_SERVER -p 5432 -U $POSTGRES_USER; do
  sleep 1
done

alembic upgrade head

uvicorn app.main:app --host 0.0.0.0 --port 8000