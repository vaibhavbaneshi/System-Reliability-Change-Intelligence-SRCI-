#!/bin/bash
set -e

echo "Waiting for Postgres to be ready..."

until psql "$DATABASE_URL" -c "SELECT 1" >/dev/null 2>&1; do
  echo "Postgres not ready yet. Retrying..."
  sleep 2
done

echo "Postgres is ready. Running SRCI database migrations..."

# Run base schema
psql "$DATABASE_URL" -f app/migrations/versions/initial_schema.sql

# Run ML feature schema
psql "$DATABASE_URL" -f app/migrations/versions/incident_change_features.sql

echo "All migrations completed successfully."