# Phase 17 — Enterprise Readiness Implementation Report

**Date:** 2026-06-20  
**Status:** Complete

---

## Summary

Phase 17 adds multi-tenant isolation, authentication/RBAC, SLA tracking, LLM cost controls, ML drift/canary monitoring, chaos validation, CI/CD, and expanded test coverage.

---

## 17.1 Multi-tenancy

- Migration: `backend/app/migrations/versions/add_phase17_enterprise.sql`
- `tenants` table with default org `00000000-0000-4000-a000-000000000001`
- `tenant_id` on `services`, `changes`, `incidents`
- PostgreSQL RLS policies using session var `app.tenant_id`
- `backend/app/db.py` — `get_connection()` sets tenant context; `get_bypass_connection()` for auth/monitor

## 17.2 RBAC

- Roles: `admin`, `analyst`, `viewer`
- Permission matrix in `backend/app/auth/rbac.py`
- Enforced in auth middleware + FastAPI `Depends(require_role(...))`

## 17.3 Authentication

- API keys: `Authorization: Bearer <key>` or `X-API-Key`
- Demo key: `srci_demo_key` (when `SRCI_AUTH_ENABLED=true`)
- Routes: `GET /auth/me`, `POST /auth/api-keys`, `GET /auth/login`
- OAuth stub: `POST /auth/oauth/callback` (enable with `SRCI_OAUTH_ENABLED=true`)
- Default: auth **disabled** for backward-compatible local demo

## 17.4 SLA Tracking

- `sla_events` table
- Auto-recorded on incident ingest, run-rca start/complete
- APIs: `GET /sla/summary`, `GET /sla/target`, `POST /sla/events`

## 17.5 LLM Cost Controls

- `llm_usage` table with token metering
- Budget per tenant (`llm_token_budget_monthly`)
- `check_budget()` in explainer — falls back to template on exceed
- API: `GET /enterprise/llm-usage`

## 17.6 Model Drift Detection

- `drift_snapshots` table
- Compares rolling feature means vs baseline (z-score threshold 2.0)
- APIs: `POST /enterprise/drift/compute`, `GET /enterprise/drift/history`

## 17.7 Canary Scoring

- `canary_predictions` table
- Re-scores with alternate rule/ML weights (`SRCI_CANARY_*` env)
- APIs: `POST /enterprise/canary/{incident_id}`, `GET /enterprise/canary/history`

## 17.8 Chaos Validation

- `chaos_runs` table
- Injects synthetic change + incident, runs RCA, checks top hypothesis
- APIs: `POST /enterprise/chaos/run` (admin), `GET /enterprise/chaos/history`

## 17.9 CI/CD

- `.github/workflows/ci.yml` — Postgres service, migrations, pytest, frontend build

## 17.10 Tests

- 34 unit tests across auth, RBAC, enterprise, guardrails, API smoke
- Scoped coverage 45%+ on auth/enterprise/reasoning modules

---

## Frontend

- `frontend/src/api/client.ts` — API key in localStorage
- Settings page — auth key input, tenant/role display, LLM budget panel

---

## How to test

```bash
# Run migration
cd backend && DATABASE_URL=postgresql://srci:srci@localhost:5432/srci bash ../scripts/run_migrations.sh

# Auth disabled (default) — existing demo works unchanged
uvicorn app.main:app --port 8001

# Auth enabled
export SRCI_AUTH_ENABLED=true
curl -H "Authorization: Bearer srci_demo_key" http://127.0.0.1:8001/auth/me

# Enterprise endpoints
curl http://127.0.0.1:8001/enterprise/llm-usage
curl http://127.0.0.1:8001/sla/summary

# Tests
cd backend && PYTHONPATH=. pytest tests/ -q --ignore=tests/test_rca_pipeline.py
```

---

## Environment variables (new)

See `.env.example` for full list. Key additions:

| Variable | Default | Purpose |
|----------|---------|---------|
| `SRCI_AUTH_ENABLED` | `false` | Require API keys |
| `SRCI_DEFAULT_TENANT_ID` | default UUID | Fallback tenant |
| `SRCI_OAUTH_ENABLED` | `false` | OAuth callback stub |
| `SRCI_LLM_COST_PER_M_TOKENS` | `0.59` | Cost estimate |
