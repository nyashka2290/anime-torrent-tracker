FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD sh -c "while ! pg_isready -h $POSTGRES_SERVER -p 5432 -U $POSTGRES_USER; do sleep 1; done && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"