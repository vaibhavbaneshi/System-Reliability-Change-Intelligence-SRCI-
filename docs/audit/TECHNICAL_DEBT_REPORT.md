# TECHNICAL_DEBT_REPORT.md

**Audit Date:** 2026-06-20  
**Severity Scale:** Critical → High → Medium → Low

---

## Critical Issues

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| C1 | **Evidence reference format mismatch** | `incident_change_correlator.py` vs `evidence_linker.py` | Correlator expects `'Change {change_id}'`; linker writes `'Deployment {git_ref} at {created_at}'`. Evidence boost **never fires**. |
| C2 | **`dependency_type` NULL on ingest** | `dependency_ingestor.py` | Dependencies inserted without `dependency_type`. `graph_traversal.py` filters on `dependency_type = ANY(...)`, returning **empty expansion** for default data. RCA and feature building silently degrade. |
| C3 | **Conflicting feature table migrations** | `add_feature_columns.sql` vs `incident_change_features.sql` | Two incompatible schemas for same table. Creates confusion about authoritative schema. Migration 2 DROP TABLE is destructive on re-run. |

---

## High Issues

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| H1 | **Open-ended change time filter in correlator** | `incident_change_correlator.py` | Uses `created_at >= incident - 24h` with **no upper bound**. Includes post-incident changes as candidates. `feature_builder.py` correctly uses `BETWEEN` with upper bound. |
| H2 | **All ML labels default to 0** | `feature_builder.py` | `label = 0` hardcoded for all feature rows. Training requires ≥2 classes; model cannot learn without external label assignment. |
| H3 | **Missing foreign keys on feature/hypothesis tables** | `incident_change_features`, `root_cause_hypotheses.change_id` | No FK from `incident_id`/`change_id` to parent tables. Orphaned rows possible. |
| H4 | **Missing indexes on hot query paths** | Schema-wide | No indexes on: `changes.created_at`, `incident_entities(incident_id)`, `change_impacts(change_id)`, `dependencies(target_id, source_id)`, `root_cause_hypotheses(incident_id, change_id)`, `evidence(incident_id)`. |
| H5 | **Migration 2 destructive on re-run** | `add_feature_columns.sql` | `DROP TABLE IF EXISTS incident_change_features` wipes all ML features on every container restart in dev. |
| H6 | **No migration versioning** | `run_migrations.sh` | No `schema_migrations` table. Cannot track applied migrations. Re-runs partially safe but unpredictable. |
| H7 | **Groq client required but unused** | `explainer.py` | `GROQ_API_KEY` required at import time. Application fails to start without it, but LLM is never called. Returns template instead. |

---

## Medium Issues

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| M1 | **Duplicate impact rows on re-propagation** | `impact_propagator.py` | No `UNIQUE(change_id, entity_type, entity_id)` constraint. Re-running propagation creates duplicate `change_impacts`. |
| M2 | **No uniqueness on features/hypotheses** | `incident_change_features`, `root_cause_hypotheses` | No `UNIQUE(incident_id, change_id)`. Duplicate rows possible under concurrency. |
| M3 | **N+1 query patterns in hot paths** | `feature_builder.py`, `incident_change_correlator.py`, `impact_propagator.py`, `predictor.py` | Per-candidate SQL round-trips. O(changes × queries) per incident RCA. |
| M4 | **Duplicated query logic** | `context_builder.py`, `explain.py`, `feature_builder.py`, `incident_change_correlator.py` | Same incident/service queries in 4 places. Bug fixes must be applied everywhere. |
| M5 | **Inconsistent graph traversal semantics** | `graph_traversal.py` vs `impact_propagator.py` | Different filters (`dependency_type` vs none), different direction assumptions. Inconsistent blast radius. |
| M6 | **`compute_hybrid_score` bypassed** | `predictor.py` vs `hybrid_scorer.py` | Reliability-calibrated fusion exists but predictor uses simpler fixed weights. |
| M7 | **DELETE-then-INSERT idempotency** | `feature_builder.py`, `incident_change_correlator.py`, `evidence_linker.py` | No history/versioning. Race conditions under concurrent requests. |
| M8 | **No pagination on list endpoints** | `services.py`, `changes_read.py`, `dependencies.py` | Unbounded result sets. |
| M9 | **Double DB connection in explain flow** | `explain.py` + `predictor.py` | Two psycopg2 connections per explanation request. |
| M10 | **No `.env.example` or README** | Repository root | Onboarding requires inferring required env vars from code. |
| M11 | **`ALTER TABLE` not idempotent** | `initial_schema.sql` | Re-running fails on `ADD COLUMN change_id` if column exists. |
| M12 | **`PROPAGATING_DEPENDENCIES` typo in compose** | `docker-compose.yml` | Set on `db` service (wrong target) with typo `runtine`. Backend uses default from `settings.py`. |

---

## Low Issues

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| L1 | **Hardcoded scoring weights scattered** | Multiple modules | 0.7/0.4/0.2, 0.6/0.4, 0.55, 0.08, 0.75/0.5 thresholds in different files. |
| L2 | **Hardcoded `REPO_PATH`** | `service_ingestor.py`, `dependency_ingestor.py` | `app/sample_repo` not configurable. |
| L3 | **Silent skip on unknown services** | `change_ingestor.py`, `incident_ingestor.py`, `dependency_ingestor.py` | Invalid service names dropped without error. |
| L4 | **No `__init__.py` files** | All Python packages | Relies on `PYTHONPATH=/app`. Works in Docker but fragile locally. |
| L5 | **`apis` and `db_tables` tables unused** | Schema only | Created but never populated by ingestion. |
| L6 | **`prompts.py` module unused** | `genai/prompts.py` | Dead code. |
| L7 | **No test suite** | Repository-wide | Zero automated tests. |
| L8 | **No CI/CD configuration** | Repository-wide | No automated build, test, or deploy pipeline. |
| L9 | **No `.dockerignore`** | `backend/` | Entire context sent to Docker daemon. |
| L10 | **Full table scan for training** | `train_model.py` | `SELECT ... FROM incident_change_features` with no WHERE/LIMIT. |

---

## Duplicate SQL Summary

| Duplication | Files | Risk |
|-------------|-------|------|
| Incident + services query | 4 files | Maintenance drift |
| Features ↔ hypotheses JOIN | 2 files | Column divergence |
| Evidence SELECT | 2 files | Identical |
| Graph traversal | 2 files | **Semantic divergence** |
| Hybrid scoring | 2 files | Feature bypass |
| Criticality mapping | SQL + Python | Parallel models |
| DELETE-then-INSERT | 3 files | Pattern duplication |

---

## Hardcoded Values Registry

| Value | Locations | Business Meaning |
|-------|-----------|------------------|
| `24` hours | `feature_builder.py`, `incident_change_correlator.py` | Candidate change lookback |
| `0.7 / 0.4 / 0.2` | `incident_change_correlator.py` | Impact level weights |
| `0.6 / 0.4` | `predictor.py` | Rule/ML fusion weights |
| `1.0 / 0.6 / 0.3` | `feature_builder.py` | Service criticality scores |
| `0.55`, `0.08` | `rca_guardrails.py` | Weak signal / close competition |
| `0.75`, `0.5` | `confidence_band.py` | Band thresholds |
| `-0.1 * hybrid_score` | `predictor.py` | Graph distance penalty |
| `app/sample_repo` | Ingestion modules | Data source path |
| `runtime,sync_api,http,grpc` | `settings.py` | Propagating dependency types |
| `label = 0` | `feature_builder.py` | All training labels unknown |

---

## Performance Risk Matrix

| Risk | Location | Mechanism | Severity |
|------|----------|-----------|----------|
| N+1 in feature build | `feature_builder.py` | Per-change SELECT | High |
| N+1 in correlation | `incident_change_correlator.py` | Per-change SELECT + COUNT | High |
| N+1 in propagation | `impact_propagator.py` | Per-node SELECT + INSERT | Medium |
| Iterative graph SQL | `graph_traversal.py` | One query per BFS level | Medium |
| Full table training scan | `train_model.py` | No LIMIT/WHERE | Low (small data) |
| Double connection | `explain.py` | Two connections per request | Low |
| Missing time index | `changes.created_at` | Seq scan on hot filter | High |
| Unbounded lists | API read endpoints | No pagination | Medium |

---

## Data Integrity Risk Matrix

| Risk | Severity | Detail |
|------|----------|--------|
| Polymorphic FK without enforcement | High | Orphaned UUIDs in `dependencies`, `change_impacts`, `incident_entities` |
| No FK on `change_id` in hypotheses | High | References non-existent changes |
| No FK on feature table | High | Orphaned feature rows |
| Duplicate propagation impacts | Medium | Inflated impact reports |
| All ML labels = 0 | High | Degenerate model |
| Evidence format mismatch | Critical | Broken scoring loop |

---

## Scalability Concerns

| Concern | Current State | Breaking Point |
|---------|---------------|----------------|
| Graph traversal | Python BFS with per-level SQL | ~1000 services, depth >5 |
| Feature building | N+1 per change candidate | ~100 changes in 24h window |
| Model training | Full table scan | ~10K feature rows |
| API listing | No pagination | ~1000 services/changes |
| Connection management | New connection per request | Concurrent load >50 |

---

## Issue Count by Severity

| Severity | Count |
|----------|-------|
| Critical | 3 |
| High | 7 |
| Medium | 12 |
| Low | 10 |
| **Total** | **32** |
