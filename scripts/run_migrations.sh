#!/bin/bash
set -e

echo "Waiting for Postgres to be ready..."

until psql "$DATABASE_URL" -c "SELECT 1" >/dev/null 2>&1; do
  echo "Postgres not ready yet. Retrying..."
  sleep 2
done

echo "Postgres is ready. Running SRCI database migrations..."

MIGRATIONS_DIR="app/migrations/versions"

psql "$DATABASE_URL" -f "$MIGRATIONS_DIR/initial_schema.sql"
psql "$DATABASE_URL" -f "$MIGRATIONS_DIR/add_feature_columns.sql"
psql "$DATABASE_URL" -f "$MIGRATIONS_DIR/add_autonomy_columns.sql"
psql "$DATABASE_URL" -f "$MIGRATIONS_DIR/add_schema_hardening.sql"
psql "$DATABASE_URL" -f "$MIGRATIONS_DIR/add_phase15_autonomy.sql"
psql "$DATABASE_URL" -f "$MIGRATIONS_DIR/add_rca_summary_columns.sql"
psql "$DATABASE_URL" -f "$MIGRATIONS_DIR/add_phase17_enterprise.sql"

echo "All migrations completed successfully."
