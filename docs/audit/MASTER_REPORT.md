# MASTER_REPORT.md

**SRCI — System Reliability & Change Intelligence**  
**Complete Project Audit**  
**Date:** 2026-06-20  
**Auditor Role:** Senior PostgreSQL Architect, Data Engineer, Legacy System Analyst

---

## 1. Architecture Overview

### What This Repository Is

SRCI (System Reliability & Change Intelligence) is a **PostgreSQL-backed FastAPI application** designed to help SREs predict change impact before deployment and explain production failures after they occur. It uses dependency graphs, rule-based correlation, ML scoring, and template-based explanations.

### System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                 Presentation Layer (NOT BUILT)                │
│            Dashboard — documented, zero code                  │
└──────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│              FastAPI REST API — 17 endpoints                  │
│   Ingest │ Changes │ Incidents │ ML │ Explain │ Reasoning    │
└──────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
   ┌─────────────┐   ┌──────────────┐   ┌─────────────┐
   │  Ingestion  │   │ Reasoning+ML │   │    GenAI     │
   │ 7 modules   │   │  8 modules   │   │  (template)  │
   └─────────────┘   └──────────────┘   └─────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│           PostgreSQL 15 — 11 tables, raw SQL migrations       │
│           No ORM │ No stored procedures │ No views            │
└──────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology |
|-----------|------------|
| Database | PostgreSQL 15 |
| Backend | Python 3.11, FastAPI, uvicorn |
| DB Access | psycopg2 (raw SQL, no ORM) |
| ML | scikit-learn (LogisticRegression), joblib |
| LLM | Groq (initialized, not invoked) |
| Containerization | Docker, Docker Compose |
| Migrations | Raw SQL via psql |

### Repository Footprint

- **55 tracked files**
- **3 SQL migration files**
- **17 API route modules**
- **7 ingestion modules**
- **8 reasoning/ML modules**
- **7 documentation files** (+ 9 audit files)
- **0 test files**
- **0 frontend files**

---

## 2. Database Overview

### Object Inventory

| Type | Count |
|------|-------|
| Tables | 11 |
| Views | 0 |
| Materialized Views | 0 |
| Sequences | 0 |
| Triggers | 0 |
| Functions | 0 |
| Stored Procedures | 0 |
| Explicit Indexes | 0 |
| Foreign Keys | 5 |
| Extensions | 1 (`uuid-ossp`) |

### Table Summary

| Table | Domain | Purpose |
|-------|--------|---------|
| `services` | Catalog | Microservice registry |
| `apis` | Catalog | API endpoint metadata (unused) |
| `db_tables` | Catalog | DB table metadata (unused) |
| `dependencies` | Graph | Service dependency edges |
| `changes` | Change | Change events (PRs, deploys) |
| `change_impacts` | Change | Change blast radius |
| `incidents` | Incident | Production failure events |
| `incident_entities` | Incident | Affected services/APIs/DBs |
| `root_cause_hypotheses` | Intelligence | Ranked change candidates |
| `evidence` | Intelligence | Supporting evidence links |
| `incident_change_features` | Intelligence | ML feature store |

### Schema Health

| Aspect | Assessment |
|--------|------------|
| Normalization | Good — clear entity separation |
| Referential integrity | Weak — polymorphic FKs, missing FKs on 3 tables |
| Indexing | Critical gap — zero explicit indexes beyond PK/UNIQUE |
| Constraints | Adequate CHECK constraints; missing UNIQUE on mappings |
| Migration hygiene | Poor — conflicting schemas, no versioning, destructive re-runs |

---

## 3. ERD Summary

The data model centers on a **dependency graph** connecting services, with two operational domains branching from it:

**Change Domain:** `changes` → `change_impacts` → services (blast radius tracking)

**Incident Domain:** `incidents` → `incident_entities` → services (failure scope)

**Intelligence Layer:** Cross-domain mapping via `root_cause_hypotheses` (rule-based) and `incident_change_features` (ML-based), linking incidents to candidate changes.

Key design pattern: **polymorphic entity references** using `(entity_type, entity_id)` tuples without database-level FK enforcement. This provides flexibility but creates orphan risk.

See `DATABASE_ERD.md` for full Mermaid diagrams.

---

## 4. Mapping Workflow

### Incident–Change Mapping

The implemented mapping workflow connects incidents to changes through a 7-step pipeline:

1. **Register services** — YAML ingestion → `services` table
2. **Build dependency graph** — `depends_on` → `dependencies` edges
3. **Record changes** — Change + direct impacts → `changes`, `change_impacts`
4. **Propagate impact** — BFS through graph → additional `change_impacts`
5. **Register incidents** — Incident + affected services → `incidents`, `incident_entities`
6. **Generate mappings** — Rule correlation + ML features → `root_cause_hypotheses`, `incident_change_features`
7. **Score and explain** — Hybrid prediction → ranked candidates with confidence bands

**Known bugs in this workflow:**
- Graph expansion broken (`dependency_type` NULL)
- Evidence boost broken (reference format mismatch)
- Time window inconsistent between correlator and feature builder

---

## 5. Technical Debt

### By Severity

| Severity | Count | Top Issues |
|----------|-------|------------|
| Critical | 3 | Evidence mismatch, dependency_type NULL, migration conflict |
| High | 7 | Time filter bug, ML labels all 0, missing FKs/indexes, destructive migrations |
| Medium | 12 | N+1 queries, duplicated logic, no pagination, unused hybrid scorer |
| Low | 10 | Hardcoded values, no tests, no CI, dead code |

### Top 5 Fixes by Impact

1. Set `dependency_type = 'runtime'` on dependency ingest
2. Align evidence reference format between correlator and linker
3. Add upper bound to correlator time window
4. Add indexes on `changes.created_at`, `change_impacts(change_id)`, `dependencies(target_id)`
5. Reconcile conflicting feature table migrations

See `TECHNICAL_DEBT_REPORT.md` for complete inventory.

---

## 6. Missing Components

### Blocking Production

| Component | Status |
|-----------|--------|
| Test suite | Missing |
| CI/CD | Missing |
| Authentication | Missing |
| README / onboarding | Missing |
| Frontend dashboard | Missing (documented only) |
| Real data ingestion (Git/logs/metrics) | Missing (YAML demo only) |
| Label assignment for ML | Missing |
| Migration versioning | Missing |

### Production Readiness: ~35%

The system demonstrates the core RCA pipeline end-to-end but requires significant hardening before production deployment.

See `PROJECT_STATUS_REPORT.md` for feature completion matrix.

---

## 7. Production Readiness Assessment

| Dimension | Score | Assessment |
|-----------|-------|------------|
| Functional completeness | 65% | Core pipeline works; known bugs |
| Data integrity | 40% | Missing FKs, indexes, constraints |
| Performance | 35% | N+1 patterns, no indexes |
| Security | 20% | No auth, no validation |
| Observability | 15% | No logging or metrics |
| Testing | 0% | No automated tests |
| Documentation | 80% | Good product docs; no README |
| **Overall** | **~35%** | MVP demo-ready |

### Can It Run Today?

**Yes** — via `docker-compose up`. The backend starts, migrations run, and all 17 API endpoints are functional with the 3-service sample repo.

### Can It Go to Production Today?

**No** — critical correctness bugs, no tests, no auth, no monitoring, no frontend, and destructive migration behavior block production deployment.

---

## 8. Recommended Next Sprint

### Sprint Goal: Stabilize Core Pipeline

**Duration:** 2 weeks

### Sprint Backlog (Priority Order)

| # | Task | Effort | Impact |
|---|------|--------|--------|
| 1 | **Fix dependency_type ingest** — set `'runtime'` default | 2 hours | Fixes graph traversal |
| 2 | **Fix evidence reference mismatch** — unify format | 2 hours | Fixes scoring boost |
| 3 | **Fix correlator time window** — add upper bound | 1 hour | Fixes candidate selection |
| 4 | **Add critical indexes** — migration for 5 indexes | 4 hours | Fixes query performance |
| 5 | **Create README + .env.example** | 2 hours | Enables onboarding |
| 6 | **Reconcile feature migrations** — remove dead migration file | 1 hour | Reduces confusion |
| 7 | **Add FK constraints** — migration for feature table + change_id | 4 hours | Data integrity |
| 8 | **Write integration test** — full ingest → correlate → predict flow | 8 hours | Establishes test foundation |
| 9 | **Consolidate context builder** — deduplicate 4 query copies | 4 hours | Maintainability |

**Estimated total:** ~28 hours (1 developer, 2 weeks with buffer)

### Sprint Exit Criteria

- All 3 critical bugs fixed and verified
- Indexes and FKs applied via new migration
- README with setup instructions exists
- At least 1 integration test passes in CI

---

## Audit Deliverables Index

| Document | Path | Contents |
|----------|------|----------|
| Repository Audit | `docs/audit/REPOSITORY_AUDIT.md` | Folder tree, file purposes, architecture |
| Database Inventory | `docs/audit/DATABASE_INVENTORY.md` | All 11 tables, constraints, columns |
| Database ERD | `docs/audit/DATABASE_ERD.md` | Mermaid ERD diagrams, relationship maps |
| Migration Audit | `docs/audit/MIGRATION_AUDIT.md` | Timeline, conflicts, rollback risks |
| Business Logic Audit | `docs/audit/BUSINESS_LOGIC_AUDIT.md` | 16 logic units with inputs/outputs/risks |
| Procedure Audit | `docs/audit/PROCEDURE_AUDIT.md` | Python procedures, dead code, duplicates |
| Technical Debt Report | `docs/audit/TECHNICAL_DEBT_REPORT.md` | 33 issues ranked by severity |
| Project Status Report | `docs/audit/PROJECT_STATUS_REPORT.md` | Completed, partial, missing features |
| Development Roadmap | `docs/audit/SRCI_ROADMAP.md` | 5-phase plan with estimates |
| **Master Report** | `docs/audit/MASTER_REPORT.md` | This document |

---

## Final Statement

This audit was performed as a **read-only analysis**. No code, migrations, or configurations were modified. The findings represent the complete state of the repository as of 2026-06-20.

**Before any implementation work begins:**

1. Fix the 3 critical correctness bugs
2. Establish migration versioning and test infrastructure
3. Confirm the development roadmap with stakeholders

The existing SRCI reliability platform has a solid architectural foundation and a working MVP pipeline. With focused stabilization work (Phase A–B of the roadmap), it can reach demo/production quality within 4–6 sprints.
