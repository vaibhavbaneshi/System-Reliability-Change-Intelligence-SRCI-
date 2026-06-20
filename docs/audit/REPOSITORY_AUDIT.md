# REPOSITORY_AUDIT.md

**Project:** SRCI — System Reliability & Change Intelligence  
**Audit Date:** 2026-06-20  
**Repository:** `System-Reliability-Change-Intelligence-SRCI-`  
**Total Tracked Files:** 55

---

## Critical Audit Finding

This repository implements **System Reliability & Change Intelligence (SRCI)** — a PostgreSQL-backed platform for service dependency graphs, change impact analysis, incident root-cause correlation, and ML-assisted hypothesis ranking.

---

## Folder Tree

```
System-Reliability-Change-Intelligence-SRCI-/
├── .gitignore
├── docker-compose.yml
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py                         # FastAPI entry point
│       ├── db.py                           # psycopg2 connection helper
│       │
│       ├── config/
│       │   └── settings.py                 # PROPAGATING_DEPENDENCIES config
│       │
│       ├── migrations/
│       │   └── versions/
│       │       ├── initial_schema.sql      # Core DDL (10 tables)
│       │       ├── add_feature_columns.sql # ML feature table (authoritative)
│       │       └── incident_change_features.sql  # Superseded alternate schema
│       │
│       ├── api/                            # 17 REST route modules
│       │   ├── ingest.py
│       │   ├── services.py
│       │   ├── dependencies.py
│       │   ├── changes.py
│       │   ├── changes_read.py
│       │   ├── change_detail.py
│       │   ├── change_impact.py
│       │   ├── impact.py
│       │   ├── incidents.py
│       │   ├── correlation.py
│       │   ├── hypotheses.py
│       │   ├── evidence.py
│       │   ├── explain.py
│       │   ├── reasoning.py
│       │   ├── features.py
│       │   ├── train.py
│       │   └── predict.py
│       │
│       ├── ingestion/                      # Data ingest pipeline
│       │   ├── service_ingestor.py
│       │   ├── dependency_ingestor.py
│       │   ├── change_ingestor.py
│       │   ├── incident_ingestor.py
│       │   ├── incident_change_correlator.py
│       │   ├── impact_propagator.py
│       │   └── evidence_linker.py
│       │
│       ├── reasoning/                      # RCA / graph reasoning
│       │   ├── graph_traversal.py
│       │   ├── context_builder.py
│       │   ├── hybrid_scorer.py
│       │   ├── confidence_band.py
│       │   └── rca_guardrails.py
│       │
│       ├── ml/                             # Feature engineering + sklearn
│       │   ├── feature_builder.py
│       │   ├── train_model.py
│       │   └── predictor.py
│       │
│       ├── genai/                          # Groq LLM explanations
│       │   ├── explainer.py
│       │   └── prompts.py
│       │
│       └── sample_repo/                    # Demo service metadata
│           ├── auth-service/service.yaml
│           ├── billing-service/service.yaml
│           └── notification-service/service.yaml
│
├── docs/
│   ├── 00_vision.md
│   ├── 01_product.md
│   ├── 02_architectural.md
│   ├── 03_modules/
│   │   ├── ingestion.md
│   │   ├── change_analysis.md
│   │   ├── incident_analysis.md
│   │   └── dashboard.md
│   └── audit/                              # This audit deliverable set
│
└── scripts/
    └── run_migrations.sh
```

---

## Root Folders

| Folder | Purpose |
|--------|---------|
| `backend/` | Python FastAPI application, PostgreSQL migrations, Docker image, dependencies |
| `docs/` | Product vision, architecture, module design, and audit documentation |
| `scripts/` | Operational shell scripts (database migration runner) |

---

## Migration Folders

**Path:** `backend/app/migrations/versions/`

| File | Lines | Purpose |
|------|-------|---------|
| `initial_schema.sql` | 130 | Base schema v1: extension, 10 core tables, `change_id` column on hypotheses |
| `add_feature_columns.sql` | 13 | DROP + CREATE `incident_change_features` with ML columns |
| `incident_change_features.sql` | 14 | Alternate feature table schema (no-op on fresh install) |

**Runner:** `scripts/run_migrations.sh` — sequential `psql` execution, no versioning table.

---

## SQL Folders

All SQL is confined to `backend/app/migrations/versions/`. There are **no** standalone query libraries, stored procedure files, or reporting SQL scripts. Business SQL is embedded in Python modules via `psycopg2`.

---

## Docker Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Orchestrates Postgres 15 (`srci-db`) + backend (`srci-backend`) with auto-migrations |
| `backend/Dockerfile` | Python 3.11-slim; installs `postgresql-client`, `curl`; runs uvicorn on port 8000 |

**Services:**

- `db` — `postgres:15`, database `srci`, user/password `srci`, port 5432, volume `pgdata`
- `backend` — builds from `./backend`, mounts `./backend` and `./scripts`, runs migrations then uvicorn with `--reload`

**Not present:** `.dockerignore`, production compose overrides, Kubernetes manifests.

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/run_migrations.sh` | Waits for Postgres readiness, runs 3 SQL migrations in fixed order |

No Makefile, CI scripts, seed scripts, or backup/restore utilities.

---

## Config Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Service orchestration, env vars, volume mounts |
| `backend/requirements.txt` | Python deps: fastapi, uvicorn, psycopg2-binary, pyyaml, groq, scikit-learn, joblib |
| `backend/app/config/settings.py` | `PROPAGATING_DEPENDENCIES` (default: `runtime,sync_api,http,grpc`) |
| `backend/app/sample_repo/*/service.yaml` | Demo service metadata for ingestion |
| `.gitignore` | Ignores `.env` |
| `.env` | Gitignored; referenced by docker-compose for secrets (`GROQ_API_KEY`) |

**Environment Variables:**

| Variable | Used In |
|----------|---------|
| `DATABASE_URL` | `db.py`, all API/ingestion modules |
| `GROQ_API_KEY` | `genai/explainer.py` (required at import, but LLM not invoked) |
| `PROPAGATING_DEPENDENCIES` | `config/settings.py`, graph traversal |

---

## Documentation Files

| File | Purpose |
|------|---------|
| `docs/00_vision.md` | Product vision, target users, non-goals |
| `docs/01_product.md` | Problem statement, workflows, MVP scope, success criteria |
| `docs/02_architectural.md` | Four-layer architecture: Ingestion, Knowledge/Graph, Intelligence, Dashboard |
| `docs/03_modules/ingestion.md` | Git/PR ingestion, schema metadata, logs/metrics/traces |
| `docs/03_modules/change_analysis.md` | Pre-deployment change impact analysis |
| `docs/03_modules/incident_analysis.md` | Post-incident RCA, causal graph, hypothesis ranking |
| `docs/03_modules/dashboard.md` | Planned UI screens (no frontend code exists) |

**Not present:** Root `README.md`, `.env.example`, API reference beyond FastAPI auto-docs, CONTRIBUTING, CHANGELOG, LICENSE.

---

## Major File Purposes

### Application Entry

| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI app, registers 17 routers, `/health` and `/` endpoints |
| `backend/app/db.py` | Database connection helper |

### API Layer (17 modules)

| Module | Route(s) | Purpose |
|--------|----------|---------|
| `ingest.py` | `POST /ingest` | Trigger service + dependency ingestion from sample repo |
| `services.py` | `GET /services` | List all services |
| `dependencies.py` | `GET /dependencies` | List dependency graph edges |
| `changes.py` | `POST /changes/ingest` | Ingest a change with touched services |
| `changes_read.py` | `GET /changes` | List all changes |
| `change_detail.py` | `GET /changes/{change_id}` | Change detail |
| `change_impact.py` | `GET /changes/{change_id}/impact` | Impacted services for a change |
| `impact.py` | `POST /changes/{change_id}/propagate` | Propagate impact through dependency graph |
| `incidents.py` | `POST /incidents/ingest` | Ingest an incident |
| `correlation.py` | `POST /incidents/{incident_id}/correlate` | Rule-based incident–change correlation |
| `hypotheses.py` | `GET /incidents/{incident_id}/hypotheses` | List root-cause hypotheses |
| `evidence.py` | `POST /incidents/{incident_id}/evidence` | Link change evidence to incident |
| `explain.py` | `GET /incidents/{incident_id}/explanation` | Generate RCA explanation |
| `reasoning.py` | `GET /incidents/{incident_id}/reasoning` | Build incident reasoning context |
| `features.py` | `POST /incidents/{incident_id}/features` | Build ML features for incident |
| `train.py` | `POST /train` | Train logistic regression model |
| `predict.py` | `POST /incidents/{incident_id}/predict` | Hybrid ML+rule predictions |

### Ingestion Pipeline

| File | Purpose |
|------|---------|
| `service_ingestor.py` | Load services from YAML with UPSERT |
| `dependency_ingestor.py` | Build service-to-service dependency edges |
| `change_ingestor.py` | Record changes and direct high-impact services |
| `incident_ingestor.py` | Create incidents and link affected services |
| `incident_change_correlator.py` | Score and persist root-cause hypotheses |
| `impact_propagator.py` | BFS blast-radius propagation for changes |
| `evidence_linker.py` | Attach deployment evidence to incidents |

### Reasoning & ML

| File | Purpose |
|------|---------|
| `graph_traversal.py` | Downstream service expansion via dependency graph |
| `context_builder.py` | Assemble incident context for reasoning APIs |
| `hybrid_scorer.py` | Reliability-calibrated rule+ML fusion (imported but bypassed in predictor) |
| `confidence_band.py` | Map hybrid scores to high/medium/low bands |
| `rca_guardrails.py` | Weak-signal and close-competition detection |
| `feature_builder.py` | Generate ML feature rows per incident–change pair |
| `train_model.py` | Train sklearn LogisticRegression on feature table |
| `predictor.py` | Hybrid scoring and ranked predictions |
| `explainer.py` | Template-based RCA narrative (Groq client initialized but unused) |

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│              (Documented, NOT implemented)                 │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                   FastAPI REST API (17 routes)           │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────────┐  ┌──────────────┐
│  Ingestion   │  │  Reasoning + ML  │  │    GenAI      │
│  (7 modules) │  │  (8 modules)     │  │  (explainer)  │
└──────────────┘  └──────────────────┘  └──────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│              PostgreSQL 15 (11 tables, raw SQL)          │
└─────────────────────────────────────────────────────────┘
```

---

## Notable Gaps

1. No root README or `.env.example`
2. No test suite, CI/CD, or lint configuration
3. No frontend/dashboard implementation (documented only)
4. No `__init__.py` files (relies on `PYTHONPATH=/app`)
5. No ORM — all SQL is raw via psycopg2
