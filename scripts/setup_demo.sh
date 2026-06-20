#!/bin/bash
# Seed SRCI with demo data and exercise every API endpoint.
# Usage: ./scripts/setup_demo.sh [BASE_URL]
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:8001}"

echo "=============================================="
echo "SRCI Demo Setup"
echo "Base URL: $BASE_URL"
echo "=============================================="

wait_for_api() {
  echo "Waiting for API..."
  for i in $(seq 1 30); do
    if curl -sf "$BASE_URL/health" >/dev/null 2>&1; then
      echo "API is ready."
      return 0
    fi
    sleep 2
  done
  echo "ERROR: API not reachable at $BASE_URL"
  exit 1
}

pretty() {
  if command -v python3 >/dev/null 2>&1; then
    python3 -m json.tool 2>/dev/null || cat
  else
    cat
  fi
}

wait_for_api

echo ""
echo "1) Health check"
curl -s "$BASE_URL/health" | pretty

echo ""
echo "2) Ingest services + dependencies (sample_repo YAML)"
curl -s -X POST "$BASE_URL/ingest" | pretty

echo ""
echo "3) List services"
curl -s "$BASE_URL/services" | pretty

echo ""
echo "4) List dependencies"
curl -s "$BASE_URL/dependencies" | pretty

echo ""
echo "5) Ingest change (auth-service deployment)"
CHANGE_RESP=$(curl -s -X POST "$BASE_URL/changes/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "change_type": "code",
    "description": "Updated auth token validation logic",
    "git_ref": "abc123def",
    "services_touched": ["auth-service"]
  }')
echo "$CHANGE_RESP" | pretty
CHANGE_ID=$(echo "$CHANGE_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['change_id'])")

# Incident must start AFTER changes for correlation window matching
sleep 2

echo ""
echo "5b) Ingest decoy change (notification-service — no billing overlap)"
curl -s -X POST "$BASE_URL/changes/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "change_type": "config",
    "description": "Notification template tweak",
    "git_ref": "notif999",
    "services_touched": ["notification-service"]
  }' | pretty

sleep 1

echo ""
echo "6) List changes"
curl -s "$BASE_URL/changes" | pretty

echo ""
echo "7) Change detail ($CHANGE_ID)"
curl -s "$BASE_URL/changes/$CHANGE_ID" | pretty

echo ""
echo "8) Change impact ($CHANGE_ID)"
curl -s "$BASE_URL/changes/$CHANGE_ID/impact" | pretty

echo ""
echo "9) Propagate change impact ($CHANGE_ID)"
curl -s -X POST "$BASE_URL/changes/$CHANGE_ID/propagate" | pretty

echo ""
echo "10) Change impact after propagation"
curl -s "$BASE_URL/changes/$CHANGE_ID/impact" | pretty

echo ""
echo "11) Ingest incident (billing-service outage)"
INCIDENT_RESP=$(curl -s -X POST "$BASE_URL/incidents/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Billing API returning 500 errors",
    "severity": "high",
    "started_at": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
    "affected_services": ["billing-service"]
  }')
echo "$INCIDENT_RESP" | pretty
INCIDENT_ID=$(echo "$INCIDENT_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['incident_id'])")

echo ""
echo "12) Correlate incident to changes ($INCIDENT_ID)"
curl -s -X POST "$BASE_URL/incidents/$INCIDENT_ID/correlate" | pretty

echo ""
echo "13) List hypotheses ($INCIDENT_ID)"
curl -s "$BASE_URL/incidents/$INCIDENT_ID/hypotheses" | pretty

echo ""
echo "14) Generate ML features ($INCIDENT_ID)"
curl -s -X POST "$BASE_URL/incidents/$INCIDENT_ID/features" | pretty

echo ""
echo "14b) Label top feature row for training (demo: mark as positive class)"
PGPASSWORD=srci psql -h localhost -U srci -d srci -c "
  UPDATE incident_change_features
  SET label = 1
  WHERE incident_id = '$INCIDENT_ID'
  AND id = (
    SELECT id FROM incident_change_features
    WHERE incident_id = '$INCIDENT_ID'
    ORDER BY service_overlap DESC, temporal_proximity DESC
    LIMIT 1
  );
" 2>/dev/null || echo "(skipped label update — run manually if train fails)"

echo ""
echo "15) Link evidence ($INCIDENT_ID)"
curl -s -X POST "$BASE_URL/incidents/$INCIDENT_ID/evidence" | pretty

echo ""
echo "16) Re-correlate (evidence boost on second pass)"
curl -s -X POST "$BASE_URL/incidents/$INCIDENT_ID/correlate" | pretty

echo ""
echo "17) Train ML model"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
rm -f "$SCRIPT_DIR/../backend/app/ml/model.joblib" 2>/dev/null || true
TRAIN_RESP=$(curl -s -X POST "$BASE_URL/train" || true)
echo "$TRAIN_RESP" | pretty

echo ""
echo "18) Predict ($INCIDENT_ID)"
curl -s -X POST "$BASE_URL/incidents/$INCIDENT_ID/predict" | pretty

echo ""
echo "19) Reasoning context ($INCIDENT_ID)"
curl -s "$BASE_URL/incidents/$INCIDENT_ID/reasoning" | pretty

echo ""
echo "20) Explanation ($INCIDENT_ID)"
curl -s "$BASE_URL/incidents/$INCIDENT_ID/explanation" | pretty

echo ""
echo "21) Orchestrated RCA — single call ($INCIDENT_ID)"
curl -s -X POST "$BASE_URL/incidents/$INCIDENT_ID/run-rca" | pretty

echo ""
echo "=============================================="
echo "Setup complete."
echo ""
echo "  CHANGE_ID   = $CHANGE_ID"
echo "  INCIDENT_ID = $INCIDENT_ID"
echo ""
echo "Re-run individual calls:"
echo "  curl $BASE_URL/incidents/$INCIDENT_ID/hypotheses"
echo "  curl -X POST $BASE_URL/incidents/$INCIDENT_ID/predict"
echo "  curl $BASE_URL/incidents/$INCIDENT_ID/explanation"
echo "=============================================="

IDS_FILE="$(cd "$(dirname "$0")/.." && pwd)/.demo_ids"
cat > "$IDS_FILE" <<EOF
BASE_URL=$BASE_URL
CHANGE_ID=$CHANGE_ID
INCIDENT_ID=$INCIDENT_ID
EOF
echo ""
echo "IDs saved to .demo_ids"
