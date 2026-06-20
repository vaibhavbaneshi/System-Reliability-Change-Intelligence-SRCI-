# SRCI Project Takeover Report

**Date:** 2026-06-20  
**Project:** SRCI — Self-Reasoning Change Intelligence  
**Repository:** `System-Reliability-Change-Intelligence-SRCI-`  
**Last Commit:** `9e10872` — *Added hybrid intelligence with explainability and guardrails*  
**Auditor Role:** Incoming development lead

---

## Executive Summary

SRCI is an AI-native SRE platform in **early MVP stage**. The core manual RCA pipeline works end-to-end via discrete REST endpoints, but the codebase **does not yet contain** most Phase 14 autonomy components described in the project brief (RCA runner, autonomous monitor, escalation engine, Prometheus metrics, retry/circuit-breaker, evaluation metrics, or `auto_rca_*` columns).

**Critical finding:** There is a significant gap between the **stated project status** (Phase 14 mostly complete) and the **actual repository state** (Phase ~12 complete with known bugs). Phase 15 should **not** begin until Phase 14 gaps are closed in code.

**Recommended immediate action:** Fix 3 critical pipeline bugs, then implement an orchestrated RCA runner with autonomy DB columns — the missing bridge between the current manual API chain and the autonomous vision.

---

## STEP 1 — What SRCI Is

### Vision (Target State)

SRCI aims to be an **Autonomous SRE Copilot** — "a senior SRE engineer that never sleeps" — capable of:

| Capability | Description |
|------------|-------------|
| Monitor | Continuously watch for production incidents |
| Correlate | Link incidents to recent changes |
| Analyze | Perform root cause analysis (RCA) |
| Rank | Score and rank likely causes |
| Explain | Communicate reasoning with confidence |
| Quantify | Estimate failure risk and blast radius |
| Escalate | Flag uncertainty for human review |
| Learn | Improve from analyst feedback |
| Operate | Run continuously without manual API calls |

### Current State (Actual)

SRCI today is a **manual, API-driven RCA backend**:

- Engineers ingest services, changes, and incidents via REST
- Each RCA step is a separate POST/GET call
- Rule-based correlation + ML hybrid scoring produce ranked hypotheses
- Template-based explanations (Groq LLM initialized but not invoked)
- No background processing, no autonomy loop, no observability stack

### Architecture Style (Confirmed)

| Property | Status |
|----------|--------|
| SQL-first schema | Yes — 3 raw SQL migrations, no ORM |
| Database-driven | Yes — PostgreSQL 15 is system of record |
| AI-native design | Partial — ML pipeline exists; LLM not wired |
| Hybrid Rule + ML | Yes — but reliability-calibrated fusion is bypassed |

### Technology Stack (Actual vs. Claimed)

| Component | Claimed | In Repo |
|-----------|---------|---------|
| FastAPI | ✓ | ✓ |
| PostgreSQL | ✓ | ✓ |
| Docker | ✓ | ✓ |
| Python | ✓ | ✓ |
| Scikit-learn | ✓ | ✓ |
| Joblib | ✓ | ✓ |
| Groq LLM | ✓ | ✓ (dependency present, not called) |
| Prometheus Metrics | ✓ | **✗ Not in requirements or code** |

---

## STEP 2 — Complete Codebase Audit

### Repository Structure

```
backend/app/
├── main.py                    # FastAPI entry, 17 routers
├── db.py                      # psycopg2 helper
├── config/settings.py         # PROPAGATING_DEPENDENCIES
├── migrations/versions/       # 3 SQL files
├── api/                       # 17 REST endpoints
├── ingestion/                 # 7 ingest/correlation modules
├── reasoning/                 # 5 modules (graph, context, scoring, guardrails)
├── ml/                        # 3 modules + model.joblib
├── genai/                     # explainer + prompts (LLM unused)
└── sample_repo/               # 3 demo services
```

**65 tracked files. 37 Python modules. 0 test files. 0 frontend.**

---

### What Exists (Implemented & Working)

| Component | Location | Notes |
|-----------|----------|-------|
| Service ingestion | `ingestion/service_ingestor.py` | YAML → `services` with UPSERT |
| Dependency ingestion | `ingestion/dependency_ingestor.py` | YAML `depends_on` → `dependencies` |
| Change ingestion | `ingestion/change_ingestor.py` | Change + direct high impacts |
| Impact propagation | `ingestion/impact_propagator.py` | BFS blast radius |
| Incident ingestion | `ingestion/incident_ingestor.py` | Incident + affected services |
| Rule-based correlation | `ingestion/incident_change_correlator.py` | Scores changes → hypotheses |
| Evidence linking | `ingestion/evidence_linker.py` | Links deployment refs to incidents |
| Graph traversal | `reasoning/graph_traversal.py` | Downstream service expansion |
| Feature engineering | `ml/feature_builder.py` | 5 ML features per incident–change pair |
| Model training | `ml/train_model.py` | LogisticRegression → `model.joblib` |
| Hybrid prediction | `ml/predictor.py` | Rule + ML fusion with decision traces |
| Confidence bands | `reasoning/confidence_band.py` | high/medium/low mapping |
| Weak signal detection | `reasoning/rca_guardrails.py` | hybrid < 0.55 |
| Close competition detection | `reasoning/rca_guardrails.py` | delta < 0.08 |
| Template explanation | `genai/explainer.py` | Markdown narrative (no LLM call) |
| Context builder | `reasoning/context_builder.py` | Incident context assembly |
| Reliability-calibrated scorer | `reasoning/hybrid_scorer.py` | **Exists but unused** |
| 17 REST API endpoints | `api/*.py` | Full manual pipeline exposed |
| Docker Compose | `docker-compose.yml` | Postgres 15 + backend |
| Core DB schema | 11 tables | See DATABASE_INVENTORY.md |

---

### What Is Partially Implemented

| Component | Status | Gap |
|-----------|--------|-----|
| **Hybrid scoring** | Partial | `compute_hybrid_score()` imported in predictor but bypassed; fixed 0.6/0.4 weights used instead |
| **Explainability** | Partial | Rich template output; Groq client initialized, never called; `prompts.py` unused |
| **Graph expansion** | Partial | Logic exists but broken for default data (`dependency_type` NULL on ingest) |
| **Evidence-aware scoring** | Partial | Boost logic exists but reference format mismatch prevents it from firing |
| **ML training** | Partial | Pipeline works; all labels default to 0 — no positive class without external labeling |
| **Blast radius** | Partial | BFS propagation for changes exists; no incident-side blast radius scoring |
| **Calibration** | Partial | `hybrid_scorer.py` has reliability calibration; not integrated into prediction path |
| **Safety controls** | Partial | Score clamping + weak/competition flags only; no retry, circuit breaker, or concurrency guards |
| **RCA pipeline** | Partial | All steps exist as separate endpoints; no orchestrated single-call workflow |

---

### What Is Missing (Claimed but Not in Codebase)

| Component | Claimed Status | Repo Reality |
|-----------|---------------|--------------|
| Prometheus metrics | ✓ Complete | **Not present** — not in requirements.txt, no `/metrics` endpoint |
| Autonomous monitor | ✓ Complete | **Not present** — no background worker or scheduler |
| RCA runner | ✓ Complete | **Not present** — no orchestrated pipeline module |
| Escalation engine | ✓ Complete | **Not present** — no escalation logic or endpoints |
| RCA quality scoring | ✓ Complete | **Not present** — only basic guardrails exist |
| Failure analysis | ✓ Complete | **Not present** — no failure analysis module |
| Evaluation metrics | ✓ Complete | **Not present** — train metrics only, no RCA evaluation |
| Batch processing controls | ✓ Complete | **Not present** |
| Retry / circuit breaker | WIP | **Not present** — zero code |
| `auto_rca_processed` columns | Expected | **Not in schema** |
| `auto_rca_processed_at` | Expected | **Not in schema** |
| `auto_rca_attempts` | Expected | **Not in schema** |
| `auto_rca_last_error` | Expected | **Not in schema** |
| Orchestrated RCA endpoint | Expected pipeline step | **Not present** |
| Evaluation pipeline step | Expected pipeline step | **Not present** |
| Autonomy loop | End-state | **Not present** |
| Frontend / dashboards | Phase 16 | **Not present** |
| Test suite | Production requirement | **0 tests** |
| CI/CD | Production requirement | **Not present** |
| Real observability ingestion | Phase 15 | **Not present** — YAML demo only |

---

### What Is Broken

| Bug | Severity | Location | Impact |
|-----|----------|----------|--------|
| **`dependency_type` NULL on ingest** | Critical | `dependency_ingestor.py` | Graph traversal returns empty expansion; RCA scores only direct overlaps |
| **Evidence reference mismatch** | Critical | `incident_change_correlator.py` vs `evidence_linker.py` | Correlator expects `'Change {id}'`; linker writes `'Deployment {ref} at {time}'`. Boost never fires |
| **Open-ended time filter in correlator** | High | `incident_change_correlator.py` | Includes post-incident changes; feature_builder correctly uses upper bound |
| **Conflicting feature migrations** | High | `add_feature_columns.sql` vs `incident_change_features.sql` | Schema drift; DROP TABLE destructive on re-run |
| **ML labels all 0** | High | `feature_builder.py` | Model cannot learn positive class |
| **Groq required but unused** | Medium | `explainer.py` | App fails without `GROQ_API_KEY` but returns template |
| **Duplicate impacts on re-propagation** | Medium | `impact_propagator.py` | No unique constraint |
| **Missing indexes** | High | Schema-wide | Hot query paths unindexed |

---

## STEP 3 — Roadmap Comparison

### Expected RCA Pipeline

```
Incident → Correlation → Evidence → Features → Prediction → Explanation → Evaluation → Autonomy
```

### Actual Pipeline (Manual)

```
POST /incidents/ingest
POST /incidents/{id}/correlate      ← separate call
POST /incidents/{id}/features       ← separate call
POST /incidents/{id}/evidence       ← separate call
POST /train                         ← separate call (global)
POST /incidents/{id}/predict        ← separate call
GET  /incidents/{id}/explanation    ← separate call
                                      ✗ Evaluation — missing
                                      ✗ Autonomy — missing
```

---

### Phase 14 — Advanced RCA Intelligence

| Component | Claimed | Actual | Status |
|-----------|---------|--------|--------|
| Correlation | ✓ | Implemented | **Complete** (with bugs) |
| Evidence | ✓ | Implemented | **Complete** (with bugs) |
| Features | ✓ | Implemented | **Complete** (labels broken) |
| Prediction | ✓ | Implemented | **Complete** (calibration bypassed) |
| Calibration | ✓ | `hybrid_scorer.py` exists | **Incomplete** — not wired |
| Explainability | ✓ | Template only | **Incomplete** — LLM not invoked |
| RCA Quality | ✓ | Not found | **Missing** |
| Failure Analysis | ✓ | Not found | **Missing** |
| Autonomy | ✓ | Not found | **Missing** |
| Safety Controls | ✓ | Guardrails only | **Incomplete** — no retry/CB |

**Phase 14 completion estimate: ~55%**

The intelligence layer (correlation, features, prediction, basic guardrails) is built. The autonomy layer (runner, monitor, escalation, evaluation, safety hardening) is **not started in code**.

---

### Can Phase 15 Begin?

**No.** Phase 15 prerequisites are not met:

| Prerequisite | Status |
|--------------|--------|
| Orchestrated RCA pipeline | Missing |
| Autonomy DB columns | Missing |
| RCA runner | Missing |
| Critical bugs fixed | Not fixed |
| Evaluation loop | Missing |
| Prometheus instrumentation | Missing (ironic — Phase 15 plans Prometheus integration) |

Phase 15 (Production Autonomy) depends on a working autonomous RCA loop. That loop does not exist yet.

---

## STEP 4 — Current Development Position

### What Was the Last Completed Step?

**Commit `9e10872` (Feb 23, 2026):** *Added hybrid intelligence with explainability and guardrails*

This commit added:
- `hybrid_scorer.py` — reliability-calibrated fusion (not yet wired)
- `confidence_band.py` — score → band mapping
- `rca_guardrails.py` — weak signal + close competition detection
- Enhanced `predictor.py` — decision traces, hybrid scoring
- Enhanced `explainer.py` — template narrative with runner-up analysis
- Enhanced `explain.py` — debug trace, RCA summary

This represents the **completion of the manual hybrid intelligence layer** — the last step before autonomy work should begin.

---

### What Is the Next Recommended Step?

**Build the orchestrated RCA runner with autonomy DB columns and critical bug fixes.**

This is the highest-priority next step because:

1. It closes the gap between manual API chain and autonomous vision
2. It provides the foundation for retry/circuit-breaker work (currently described as WIP but not started)
3. It unblocks Phase 14 completion before Phase 15 can begin
4. Critical bugs must be fixed first or the runner will produce incorrect results

---

### Files That Need Modification

#### Immediate (Critical Bug Fixes)

| File | Change |
|------|--------|
| `backend/app/ingestion/dependency_ingestor.py` | Set `dependency_type = 'runtime'` on INSERT |
| `backend/app/ingestion/incident_change_correlator.py` | Fix time window upper bound; fix evidence reference format |
| `backend/app/ingestion/evidence_linker.py` | Align reference format with correlator (or vice versa) |
| `docker-compose.yml` | Fix `PROPAGATING_DEPENDENCIES` typo; move to backend service |

#### Next (RCA Runner + Autonomy)

| File | Change |
|------|--------|
| `backend/app/migrations/versions/add_autonomy_columns.sql` | **New** — `auto_rca_*` columns on `incidents` |
| `backend/app/autonomy/rca_runner.py` | **New** — orchestrated pipeline |
| `backend/app/autonomy/safety.py` | **New** — retry + circuit breaker |
| `backend/app/api/rca.py` | **New** — `POST /incidents/{id}/run-rca` |
| `backend/app/main.py` | Register new router |
| `scripts/run_migrations.sh` | Add new migration |
| `backend/app/ml/predictor.py` | Wire `compute_hybrid_score()` |
| `backend/app/genai/explainer.py` | Wire Groq LLM call (optional, Phase 14 completion) |

#### Soon (Hardening)

| File | Change |
|------|--------|
| `backend/app/migrations/versions/add_indexes.sql` | **New** — performance indexes |
| `backend/requirements.txt` | Add `prometheus-client` |
| `backend/app/main.py` | Add `/metrics` endpoint |
| `tests/` | **New** — integration test for full RCA pipeline |

---

### Technical Debt (Priority Order)

| # | Issue | Severity |
|---|-------|----------|
| 1 | No orchestrated pipeline | Critical — blocks autonomy |
| 2 | `dependency_type` NULL | Critical — breaks graph |
| 3 | Evidence reference mismatch | Critical — breaks scoring |
| 4 | No autonomy DB columns | Critical — blocks runner state |
| 5 | No tests | High — no regression safety |
| 6 | Hybrid scorer bypassed | High — calibration unused |
| 7 | ML labels all 0 | High — model degenerate |
| 8 | Missing indexes/FKs | High — performance + integrity |
| 9 | Destructive migrations | High — data loss on re-run |
| 10 | N+1 query patterns | Medium — performance |
| 11 | Duplicated context queries | Medium — maintenance |
| 12 | Groq required but unused | Medium — startup failure risk |
| 13 | No pagination | Low |
| 14 | No README | Low |

---

### Architectural Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Vision-code gap** | Team may assume Phase 14 is done; autonomy work hasn't started | This report; align status tracking with repo |
| **Manual-only pipeline** | Cannot operate continuously; every step requires human API calls | Build RCA runner first |
| **No concurrency control** | Parallel RCA runs on same incident will race (DELETE-then-INSERT) | Distributed locking in runner |
| **Polymorphic FKs** | Orphaned UUIDs possible; no referential integrity on graph edges | Add FK constraints where possible |
| **Single-process architecture** | No worker model; uvicorn only | Phase 15 multi-worker design |
| **Model not versioned** | `model.joblib` committed to git; no model registry | Externalize model artifact |
| **No idempotent migrations** | Container restart can DROP feature table | Migration versioning + non-destructive alters |

---

## STEP 5 — Development Restart Plan

### Phase 0: Stabilize (Sprint 1, ~1 week)

**Goal:** Fix correctness bugs so the pipeline produces accurate results.

| Task | Files | DB Changes | Tests |
|------|-------|------------|-------|
| Fix `dependency_type` ingest | `dependency_ingestor.py` | None | Unit: graph traversal returns expanded services |
| Fix evidence reference format | `correlator.py`, `evidence_linker.py` | None | Unit: evidence boost fires |
| Fix correlator time window | `incident_change_correlator.py` | None | Unit: post-incident changes excluded |
| Reconcile feature migrations | Remove dead migration file | None | Migration smoke test |
| Add critical indexes | New migration SQL | 5 indexes | None |
| Create README + `.env.example` | Root | None | None |

**Exit criteria:** Full manual pipeline produces correct scores on sample data.

---

### Phase 1: RCA Runner (Sprint 2, ~1 week)

**Goal:** Single-call orchestrated pipeline — the bridge to autonomy.

| Task | Files | DB Changes | Tests |
|------|-------|------------|-------|
| Add autonomy columns migration | `add_autonomy_columns.sql` | `auto_rca_processed`, `auto_rca_processed_at`, `auto_rca_attempts`, `auto_rca_last_error`, `auto_rca_in_progress` on `incidents` | Migration test |
| Build RCA runner | `autonomy/rca_runner.py` | None | Integration: full pipeline |
| Add run-rca endpoint | `api/rca.py`, `main.py` | None | API test |
| Wire hybrid scorer | `predictor.py` | None | Unit: calibration applied |
| Integration test | `tests/test_rca_pipeline.py` | None | End-to-end |

**Pipeline the runner executes:**

```
1. correlate_incident_to_changes()
2. build_features_for_incident()
3. link_change_evidence()
4. predict_for_incident()
5. generate_explanation()
6. Update auto_rca_* columns
```

**Exit criteria:** `POST /incidents/{id}/run-rca` returns full RCA result in one call.

---

### Phase 2: Safety Hardening (Sprint 3, ~1 week)

**Goal:** Complete Phase 14 autonomy and safety controls.

| Task | Files | DB Changes | Tests |
|------|-------|------------|-------|
| Retry with backoff | `autonomy/safety.py` | None | Unit: retry on transient failure |
| Circuit breaker | `autonomy/safety.py` | None | Unit: breaker opens after N failures |
| Concurrency guard | `autonomy/rca_runner.py` | Uses `auto_rca_in_progress` | Unit: duplicate run rejected |
| Escalation on weak signal | `autonomy/escalation.py` | Optional escalation table | Unit: weak RCA flagged |
| RCA quality scoring | `reasoning/rca_quality.py` | None | Unit: quality score computed |
| Prometheus metrics | `main.py`, `requirements.txt` | None | Smoke: `/metrics` returns data |

**Exit criteria:** Phase 14 checklist complete. Phase 15 can begin.

---

### Phase 3: Begin Phase 15 (Sprint 4+)

Only after Phase 0–2 are complete:

- Event-driven processing (incident webhook → auto RCA)
- Background monitor polling for unprocessed incidents
- Learning loop (analyst feedback → label assignment)
- External integrations (PagerDuty, Datadog, OpenTelemetry)

---

## Immediate Next Task (Do This First)

### Task: Fix `dependency_type` on dependency ingest

**Why highest priority:** Every downstream RCA step that uses graph expansion (`graph_traversal.py`, correlation, feature building) silently fails for default data. This is the single bug with the widest blast radius across the pipeline.

**Required code change:**

```
File: backend/app/ingestion/dependency_ingestor.py
Change: INSERT must include dependency_type = 'runtime'
```

**Required DB change:** None (column already exists).

**Required test:**

```python
# tests/test_dependency_ingest.py
# After ingest, graph_traversal must return >1 service for billing-service incident
```

**Estimated effort:** 2 hours including test.

**Then immediately:** Fix evidence reference mismatch (2 hours) and correlator time window (1 hour).

---

## Appendix A — API Reference (Current)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/ingest` | Ingest services + dependencies from sample repo |
| GET | `/services` | List services |
| GET | `/dependencies` | List dependency edges |
| POST | `/changes/ingest` | Ingest a change |
| GET | `/changes` | List changes |
| GET | `/changes/{id}` | Change detail |
| GET | `/changes/{id}/impact` | Change blast radius |
| POST | `/changes/{id}/propagate` | Propagate impact through graph |
| POST | `/incidents/ingest` | Ingest an incident |
| POST | `/incidents/{id}/correlate` | Rule-based correlation |
| GET | `/incidents/{id}/hypotheses` | List hypotheses |
| POST | `/incidents/{id}/evidence` | Link evidence |
| POST | `/incidents/{id}/features` | Build ML features |
| POST | `/train` | Train ML model |
| POST | `/incidents/{id}/predict` | Hybrid prediction |
| GET | `/incidents/{id}/explanation` | RCA explanation |
| GET | `/incidents/{id}/reasoning` | Reasoning context |
| GET | `/health` | Health check |

**Missing from expected pipeline:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/incidents/{id}/run-rca` | Orchestrated full pipeline |
| POST | `/incidents/{id}/evaluate` | RCA quality evaluation |
| GET | `/metrics` | Prometheus metrics |

---

## Appendix B — Git History (Build Sequence)

| Commit | Milestone |
|--------|-----------|
| `934cd8d` | Foundational schema |
| `a4cb2f8` | Service + dependency ingestor |
| `672f09b` | Read-only APIs |
| `e734358` | Change model |
| `a09516c` | Change impact + blast radius |
| `7380fe9` | Incident ingestion |
| `814346a` | GenAI explanation pipeline |
| `347645a` | Evidence-aware correlation |
| `94e0307` | Graph-based propagation |
| `7608701` | ML pipeline |
| `192a828` | Feature pipeline + training + prediction |
| `9e10872` | **Hybrid intelligence + guardrails** ← current position |

---

## Appendix C — Phase Completion Matrix

| Phase | Description | Completion |
|-------|-------------|------------|
| 1–10 | Schema, ingest, APIs, changes | 100% |
| 11 | Incident ingestion | 100% |
| 12 | Correlation + evidence | 90% (bugs) |
| 13 | ML pipeline | 85% (labels, calibration) |
| 14 | Advanced RCA + autonomy | **55%** |
| 15 | Production autonomy | 0% |
| 16 | SRE Copilot UI | 0% |
| 17 | Enterprise readiness | 0% |

---

## Final Recommendation

Do **not** begin Phase 15 integration work. Do **not** write new features until the 3 critical bugs are fixed.

**Restart sequence:**

1. Fix critical bugs (3 days)
2. Build RCA runner + autonomy columns (5 days)
3. Add safety controls + Prometheus (5 days)
4. Write integration tests (3 days)
5. Then begin Phase 15

This positions the project to honestly claim Phase 14 complete within ~3 weeks of focused development.
