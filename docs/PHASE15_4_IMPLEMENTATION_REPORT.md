# Phase 15.4 — Advanced Graph Intelligence Report

**Date:** 2026-06-20  
**Status:** Complete

---

## Summary

Phase 15.4 adds dependency-aware blast radius estimation, upstream/downstream graph analysis, probabilistic failure spread, PostgreSQL recursive CTE traversal, weighted impact propagation, and failure risk panel APIs.

---

## Backend

### Migration
`backend/app/migrations/versions/add_phase15_4_graph.sql`
- `srci_graph_downstream(seed_ids, max_depth)` — recursive CTE
- `srci_graph_upstream(seed_ids, max_depth)` — recursive CTE
- `change_blast_radius` cache table

### Core modules
- `backend/app/graph/blast_radius.py` — blast radius, risk panel, failure spread
- `backend/app/graph/impact_propagation.py` — weighted propagate + auto-compute
- `backend/app/config/settings.py` — `DEPENDENCY_TYPE_WEIGHTS`, depth decay

### APIs
| Method | Path | Description |
|--------|------|-------------|
| GET | `/changes/{id}/blast-radius` | Full blast radius analysis |
| POST | `/changes/{id}/blast-radius/compute` | Recompute and persist |
| POST | `/changes/{id}/propagate` | Weighted impact propagation |
| GET | `/services/{id}/failure-risk` | Hypothetical failure risk panel |
| POST | `/changes/ingest` | Now returns blast radius summary |

---

## Frontend

- `ChangeImpactPage` — blast score, risk band, failure spread, upstream/downstream lists
- `changesApi.blastRadius()` + `servicesApi.failureRisk()`

---

## How to test

```bash
cd backend
export DATABASE_URL=postgresql://srci:srci@localhost:5432/srci
bash ../scripts/run_migrations.sh

python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8001

curl http://127.0.0.1:8001/changes/{CHANGE_ID}/blast-radius
curl http://127.0.0.1:8001/services/{SERVICE_ID}/failure-risk
curl -X POST http://127.0.0.1:8001/changes/{CHANGE_ID}/propagate
```

Frontend: `/changes/{id}/impact`

---

## Tests

`backend/tests/test_graph_intelligence.py` — 8 unit tests (42 total pass)
