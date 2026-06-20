# SRCI Development Roadmap

**Living document — update this file as work completes.**  
**Last updated:** 2026-06-20 (Phase 14 sprint 3)  
**North star:** Autonomous SRE Copilot — *"a senior SRE engineer that never sleeps."*

---

## How to use this roadmap

1. **Before starting work** — find the next `[ ]` item in the current phase.
2. **When you finish a task** — change `[ ]` → `[x]` and add a date in the *Done* column.
3. **When scope changes** — add new rows or phases at the bottom; don't delete history.
4. **Weekly** — update the [Progress Summary](#progress-summary) counts.

Related docs (audit snapshots, not living):
- [`docs/audit/TAKEOVER_REPORT.md`](audit/TAKEOVER_REPORT.md) — codebase truth at takeover
- [`docs/audit/MASTER_REPORT.md`](audit/MASTER_REPORT.md) — architecture audit

---

## Progress Summary

| Phase | Name | Status | Done | Total | % |
|-------|------|--------|------|-------|---|
| 0–13 | Foundation & MVP pipeline | Mostly complete | 28 | 30 | 93% |
| 14 | Advanced RCA Intelligence | **In progress** | 27 | 32 | 84% |
| 15 | Production Autonomy | Not started | 0 | 12 | 0% |
| 15.4 | Advanced Graph Intelligence | Not started | 0 | 6 | 0% |
| 16 | SRE Copilot Experience | Not started | 0 | 10 | 0% |
| 17 | Enterprise Readiness | Not started | 0 | 10 | 0% |
| — | Dev hygiene (parallel) | In progress | 3 | 10 | 30% |

**Current focus:** Phase 14 — finish intelligence (quality scoring, evaluation)  
**Next task:** 14.3.8 — RCA quality scoring module

---

## End-state vision

SRCI should continuously:

- Monitor production incidents
- Correlate incidents with changes
- Perform root cause analysis (RCA)
- Rank likely causes with confidence
- Explain reasoning
- Estimate failure risk & blast radius
- Escalate when uncertain
- Learn from analyst feedback

**Target RCA pipeline:**

```
Incident → Correlation → Evidence → Features → Prediction → Explanation → Evaluation → Autonomy
```

---

## Phases 0–13 — Foundation (built before Phase 14)

> Historical baseline. Most of this exists in the repo today.

### Infrastructure & schema

| Done | ID | Task | Notes |
|:----:|----|------|-------|
| [x] | 0.1 | Docker Compose (Postgres 15 + backend) | `docker-compose.yml` |
| [x] | 0.2 | Raw SQL migrations runner | `scripts/run_migrations.sh` |
| [x] | 0.3 | Core schema (11 tables) | `initial_schema.sql` + feature table |
| [x] | 0.4 | FastAPI app + health check | `main.py` |
| [ ] | 0.5 | Migration versioning table | No `schema_migrations` yet |
| [ ] | 0.6 | Root README + `.env.example` | Missing |

### Ingestion & graph

| Done | ID | Task | Notes |
|:----:|----|------|-------|
| [x] | 1.1 | Service ingestion (YAML UPSERT) | `service_ingestor.py` |
| [x] | 1.2 | Dependency graph ingestion | `dependency_ingestor.py` |
| [x] | 1.3 | Change ingestion | `change_ingestor.py` |
| [x] | 1.4 | Impact propagation (BFS) | `impact_propagator.py` |
| [x] | 1.5 | Incident ingestion | `incident_ingestor.py` |
| [x] | 1.6 | Sample repo (3 services) | `sample_repo/` |
| [ ] | 1.7 | Real Git/PR ingestion | Documented only |
| [ ] | 1.8 | Log/metric/trace ingestion | Documented only |

### Read APIs

| Done | ID | Task | Notes |
|:----:|----|------|-------|
| [x] | 2.1 | `GET /services` | |
| [x] | 2.2 | `GET /dependencies` | |
| [x] | 2.3 | `GET /changes`, `GET /changes/{id}` | |
| [x] | 2.4 | `GET /changes/{id}/impact` | |
| [x] | 2.5 | `POST /ingest` | |

### RCA pipeline (manual, per-step APIs)

| Done | ID | Task | Notes |
|:----:|----|------|-------|
| [x] | 3.1 | Rule-based correlation | `incident_change_correlator.py` |
| [x] | 3.2 | Evidence linking | `evidence_linker.py` |
| [x] | 3.3 | ML feature generation | `feature_builder.py` |
| [x] | 3.4 | Model training | `train_model.py` |
| [x] | 3.5 | Hybrid prediction | `predictor.py` |
| [x] | 3.6 | Confidence bands | `confidence_band.py` |
| [x] | 3.7 | Weak signal + close competition guardrails | `rca_guardrails.py` |
| [x] | 3.8 | Template explanation | `explainer.py` (template, not LLM) |
| [x] | 3.9 | Reasoning context API | `context_builder.py` |
| [x] | 3.10 | Graph downstream traversal | `graph_traversal.py` |

### Demo & local dev tooling

| Done | ID | Task | Notes |
|:----:|----|------|-------|
| [x] | 4.1 | Demo setup script | `scripts/setup_demo.sh` |
| [x] | 4.2 | Demo reset script | `scripts/reset_demo.sh` |

**Phase 0–13 exit criteria:** Manual RCA works end-to-end via separate API calls. ✅ *Achieved 2026-06-20*

---

## Phase 14 — Advanced RCA Intelligence

**Goal:** Complete the intelligence layer and add autonomy foundations.  
**Status:** In progress (~75%)  
**Exit criteria:** Single-call RCA, calibration wired, quality scoring, safety controls, autonomy columns.

### 14.1 — Correctness & stabilization

| Done | ID | Task | Notes |
|:----:|----|------|-------|
| [x] | 14.1.1 | Fix `dependency_type` on dependency ingest | 2026-06-20 — default `runtime` |
| [x] | 14.1.2 | Fix evidence reference format mismatch | 2026-06-20 — shared `format_change_evidence_reference()` |
| [x] | 14.1.3 | Fix correlator 24h time window upper bound | 2026-06-20 — `BETWEEN` filter |
| [x] | 14.1.4 | Reconcile conflicting feature table migrations | 2026-06-20 — removed dead migration |
| [x] | 14.1.5 | Fix docker-compose `PROPAGATING_DEPENDENCIES` typo | 2026-06-20 — moved to backend service |

### 14.2 — Schema hardening

| Done | ID | Task | Notes |
|:----:|----|------|-------|
| [x] | 14.2.1 | Add indexes on hot query paths | `add_schema_hardening.sql` |
| [x] | 14.2.2 | FK on `incident_change_features` | |
| [x] | 14.2.3 | FK on `root_cause_hypotheses.change_id` | |
| [x] | 14.2.4 | Unique constraints on mappings | features, hypotheses, impacts |

### 14.3 — Intelligence completion

| Done | ID | Task | Notes |
|:----:|----|------|-------|
| [x] | 14.3.1 | Correlation engine | |
| [x] | 14.3.2 | Evidence generation | |
| [x] | 14.3.3 | Feature generation | |
| [x] | 14.3.4 | Hybrid prediction + decision traces | |
| [x] | 14.3.5 | Wire `compute_hybrid_score()` calibration | 2026-06-20 — predictor uses calibrated fusion |
| [x] | 14.3.6 | Activate Groq LLM in explainer | 2026-06-20 — Groq with template fallback |
| [x] | 14.3.7 | Label assignment pipeline | 2026-06-20 — `POST /incidents/{id}/labels` |
| [ ] | 14.3.8 | RCA quality scoring module | Not built |
| [ ] | 14.3.9 | Failure analysis module | Not built |
| [ ] | 14.3.10 | Evaluation metrics endpoint | Not built |

### 14.4 — Orchestrated RCA (autonomy bridge)

| Done | ID | Task | Notes |
|:----:|----|------|-------|
| [x] | 14.4.1 | **`POST /incidents/{id}/run-rca`** — single-call pipeline | 2026-06-20 |
| [x] | 14.4.2 | `autonomy/rca_runner.py` — orchestrate all steps | |
| [x] | 14.4.3 | Return unified RCA response (predict + explain + trace) | |

### 14.5 — Autonomy database columns

| Done | ID | Task | Notes |
|:----:|----|------|-------|
| [x] | 14.5.1 | Migration: `auto_rca_processed` | `add_autonomy_columns.sql` |
| [x] | 14.5.2 | Migration: `auto_rca_processed_at` | |
| [x] | 14.5.3 | Migration: `auto_rca_attempts` | |
| [x] | 14.5.4 | Migration: `auto_rca_last_error` | |
| [x] | 14.5.5 | Migration: `auto_rca_in_progress` | concurrency guard |

### 14.6 — Safety controls

| Done | ID | Task | Notes |
|:----:|----|------|-------|
| [x] | 14.6.1 | Score clamping guardrails | `rca_guardrails.py` |
| [x] | 14.6.2 | Weak signal detection | |
| [x] | 14.6.3 | Close competition detection | |
| [x] | 14.6.4 | Retry with backoff | `autonomy/safety.py` |
| [x] | 14.6.5 | Circuit breaker | in-process breaker on runner |
| [ ] | 14.6.6 | Batch processing controls | Not built |
| [x] | 14.6.7 | Escalation engine (weak RCA → flag) | 2026-06-20 — `reasoning/escalation.py` |

### 14.7 — Code consolidation

| Done | ID | Task | Notes |
|:----:|----|------|-------|
| [x] | 14.7.1 | Consolidate explanation builder | `reasoning/explanation_builder.py` |
| [ ] | 14.7.2 | Unify graph traversal semantics | propagator vs `graph_traversal.py` |
| [ ] | 14.7.3 | Centralize scoring weights | config or DB table |
| [ ] | 14.7.4 | Batch SQL (replace N+1 loops) | feature_builder, correlator |

**Phase 14 exit criteria:** `run-rca` works; autonomy columns populated; retry/CB on runner; quality + evaluation endpoints exist.

---

## Phase 15 — Production Autonomy

**Goal:** Run continuously without manual API calls; integrate with observability stack.  
**Status:** Not started  
**Depends on:** Phase 14 complete

| Done | ID | Task | Notes |
|:----:|----|------|-------|
| [ ] | 15.1 | Autonomous monitor (poll unprocessed incidents) | Background worker |
| [ ] | 15.2 | Event-driven processing (webhook on incident ingest) | |
| [ ] | 15.3 | Multi-worker concurrency | |
| [ ] | 15.4 | Distributed locking | Prevent duplicate RCA runs |
| [ ] | 15.5 | Prometheus `/metrics` endpoint | |
| [ ] | 15.6 | Grafana dashboards | |
| [ ] | 15.7 | PagerDuty integration | Escalation delivery |
| [ ] | 15.8 | Datadog integration | Metrics/logs ingest |
| [ ] | 15.9 | OpenTelemetry ingestion | Traces |
| [ ] | 15.10 | Learning loop | Feedback → labels → retrain |
| [ ] | 15.11 | Online feedback collection API | Analyst confirms/rejects RCA |
| [ ] | 15.12 | Production Docker Compose | No `--reload`, health checks |

**Phase 15 exit criteria:** New incident auto-triggers RCA; metrics visible in Grafana; weak RCAs escalate to PagerDuty.

---

## Phase 15.4 — Advanced Graph Intelligence

**Goal:** Deep dependency-aware impact modeling.  
**Status:** Not started  
**Depends on:** Phase 14.2 schema hardening

| Done | ID | Task | Notes |
|:----:|----|------|-------|
| [ ] | 15.4.1 | Blast radius estimation API | Beyond BFS depth levels |
| [ ] | 15.4.2 | Upstream/downstream scoring | Directional graph analysis |
| [ ] | 15.4.3 | Failure spread modeling | Probabilistic propagation |
| [ ] | 15.4.4 | Graph traversal as PostgreSQL function | Recursive CTE |
| [ ] | 15.4.5 | Impact propagation with `dependency_type` weights | |
| [ ] | 15.4.6 | Failure risk quantification panel data | API for dashboards |

**Phase 15.4 exit criteria:** Change submit returns estimated blast radius with upstream/downstream breakdown.

---

## Phase 16 — SRE Copilot Experience

**Goal:** Human-facing product — dashboards and conversational RCA.  
**Status:** Not started  
**Depends on:** Phase 15 metrics + Phase 14 run-rca

| Done | ID | Task | Notes |
|:----:|----|------|-------|
| [ ] | 16.1 | Incident dashboard | See `docs/03_modules/dashboard.md` |
| [ ] | 16.2 | RCA dashboard | Hypothesis ranking UI |
| [ ] | 16.3 | Confidence visualizations | Bands, traces, feature vectors |
| [ ] | 16.4 | Failure risk panels | |
| [ ] | 16.5 | Dependency graph visualization | Interactive |
| [ ] | 16.6 | Change impact report UI | Blast radius visual |
| [ ] | 16.7 | Human review workflow | Confirm/reject/correct RCA |
| [ ] | 16.8 | RCA chat interface | *"Why is billing failing?"* |
| [ ] | 16.9 | Weak RCA queue view | *"Show weak RCAs today"* |
| [ ] | 16.10 | Change timeline view | *"What changed before this outage?"* |

**Phase 16 exit criteria:** SRE can investigate an incident entirely through the UI without curl.

---

## Phase 17 — Enterprise Readiness

**Goal:** Multi-team production deployment.  
**Status:** Not started

| Done | ID | Task | Notes |
|:----:|----|------|-------|
| [ ] | 17.1 | Multi-tenancy | Tenant isolation |
| [ ] | 17.2 | RBAC | Role-based access |
| [ ] | 17.3 | Authentication (API keys / OAuth) | |
| [ ] | 17.4 | SLA tracking | |
| [ ] | 17.5 | Cost controls | LLM token budgets |
| [ ] | 17.6 | Model drift detection | ML monitoring |
| [ ] | 17.7 | Canary scoring | Shadow predictions |
| [ ] | 17.8 | Chaos validation | Synthetic failure injection |
| [ ] | 17.9 | CI/CD pipeline | GitHub Actions |
| [ ] | 17.10 | 80%+ test coverage | Unit + integration |

**Phase 17 exit criteria:** Production deployment with auth, tenancy, CI green, drift monitoring.

---

## Dev hygiene (parallel track)

Work that spans all phases — pick these up alongside the current phase.

| Done | ID | Task | Notes |
|:----:|----|------|-------|
| [x] | H.1 | Integration test: full RCA pipeline | `backend/tests/test_rca_pipeline.py` |
| [ ] | H.2 | Unit tests for scoring/guardrails | |
| [ ] | H.3 | Structured logging | Request + query timing |
| [ ] | H.4 | Connection pooling | pgBouncer or psycopg2 pool |
| [ ] | H.5 | Pagination on list APIs | |
| [ ] | H.6 | Input validation (Pydantic) | All POST bodies |
| [ ] | H.7 | Replace DELETE-then-INSERT with UPSERT | Preserve history |
| [ ] | H.8 | Database views for reporting | |
| [ ] | H.9 | Secrets management | Vault / env injection |
| [ ] | H.10 | Rate limiting | |

---

## Suggested development order (next 6 sprints)

| Sprint | Focus | Key deliverables |
|--------|-------|------------------|
| **1** ✅ | Stabilize | 3 bug fixes, demo scripts |
| **2** ✅ | RCA runner | 14.4 + 14.5 + 14.3.5 + schema hardening |
| **3** | Intelligence finish | 14.3.6–10, 14.6.7, 14.7 |
| **4** | Intelligence | 14.3.6–10, 14.7 |
| **5** | Autonomy | Phase 15.1–15.5 |
| **6** | Observability | Phase 15.6–15.12 |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-20 | Roadmap created. Phase 14.1.1–14.1.3 marked done. Demo scripts added. |
| 2026-06-20 | Phase 14 sprint: run-rca endpoint, rca_runner, autonomy columns, schema hardening, calibrated hybrid scorer, retry/CB, explanation builder. |
| 2026-06-20 | Sprint 3: Groq LLM explainer (template fallback), label assignment API, escalation engine. |
| | *Add new rows here as phases expand.* |

---

## Adding new phases

When you need to extend the roadmap:

1. Add a new `## Phase N — Title` section above *Changelog*.
2. Use checkbox tables with unique IDs (e.g. `18.1`, `18.2`).
3. Update the [Progress Summary](#progress-summary) table.
4. Log the addition in *Changelog*.

**ID convention:** `{phase}.{section}.{item}` — e.g. `14.4.1` = Phase 14, section 4 (orchestrated RCA), item 1.
