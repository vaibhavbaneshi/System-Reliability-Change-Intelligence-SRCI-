#!/bin/bash
# Reset SRCI demo data (keeps schema intact).
set -euo pipefail

DATABASE_URL="${DATABASE_URL:-postgresql://srci:srci@localhost:5432/srci}"

echo "Resetting SRCI demo data..."
psql "$DATABASE_URL" -c "
  TRUNCATE
    incident_change_features,
    evidence,
    root_cause_hypotheses,
    incident_entities,
    incidents,
    change_impacts,
    changes,
    dependencies,
    apis,
    db_tables,
    services
  RESTART IDENTITY CASCADE;
"
echo "Done."
