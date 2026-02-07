#!/bin/bash
set -e

echo "Waiting for Postgres to be ready..."

until psql "$DATABASE_URL" -c "SELECT 1" >/dev/null 2>&1; do
  echo "Postgres not ready yet. Retrying..."
  sleep 2
done

echo "Postgres is ready. Running SRCI database migrations..."

psql "$DATABASE_URL" -f app/migrations/versions/initial_schema.sql

echo "Migrations completed successfully."