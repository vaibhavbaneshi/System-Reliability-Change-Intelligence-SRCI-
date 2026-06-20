-- ================================
-- Phase 17 — Enterprise Readiness
-- Multi-tenancy, auth, SLA, LLM budgets, drift, canary, chaos
-- ================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ================================
-- TENANTS
-- ================================
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    plan TEXT NOT NULL DEFAULT 'standard' CHECK (plan IN ('standard', 'enterprise')),
    llm_token_budget_monthly INTEGER NOT NULL DEFAULT 100000,
    sla_target_minutes INTEGER DEFAULT 60,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO tenants (id, name, slug, plan, llm_token_budget_monthly, sla_target_minutes, created_at)
VALUES (
    '00000000-0000-4000-a000-000000000001',
    'Default Organization',
    'default',
    'enterprise',
    500000,
    60,
    NOW()
) ON CONFLICT (id) DO NOTHING;

-- ================================
-- USERS & RBAC
-- ================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    display_name TEXT,
    role TEXT NOT NULL DEFAULT 'analyst'
        CHECK (role IN ('admin', 'analyst', 'viewer')),
    oauth_provider TEXT,
    oauth_subject TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, email)
);

CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    name TEXT NOT NULL DEFAULT 'default',
    key_prefix TEXT NOT NULL,
    key_hash TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL DEFAULT 'analyst'
        CHECK (role IN ('admin', 'analyst', 'viewer')),
    expires_at TIMESTAMP,
    revoked_at TIMESTAMP,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_api_keys_prefix ON api_keys(key_prefix);
CREATE INDEX IF NOT EXISTS idx_api_keys_tenant ON api_keys(tenant_id);

INSERT INTO users (id, tenant_id, email, display_name, role)
VALUES (
    '00000000-0000-4000-a000-000000000002',
    '00000000-0000-4000-a000-000000000001',
    'admin@srci.local',
    'SRCI Admin',
    'admin'
) ON CONFLICT DO NOTHING;

-- Demo API key plaintext: srci_demo_key
INSERT INTO api_keys (id, tenant_id, user_id, name, key_prefix, key_hash, role)
VALUES (
    '00000000-0000-4000-a000-000000000003',
    '00000000-0000-4000-a000-000000000001',
    '00000000-0000-4000-a000-000000000002',
    'demo',
    'srci_demo',
    encode(digest('srci_demo_key', 'sha256'), 'hex'),
    'admin'
) ON CONFLICT DO NOTHING;

-- ================================
-- TENANT COLUMNS ON ROOT ENTITIES
-- ================================
ALTER TABLE services ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES tenants(id);
ALTER TABLE changes ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES tenants(id);
ALTER TABLE incidents ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES tenants(id);

UPDATE services SET tenant_id = '00000000-0000-4000-a000-000000000001' WHERE tenant_id IS NULL;
UPDATE changes SET tenant_id = '00000000-0000-4000-a000-000000000001' WHERE tenant_id IS NULL;
UPDATE incidents SET tenant_id = '00000000-0000-4000-a000-000000000001' WHERE tenant_id IS NULL;

ALTER TABLE services ALTER COLUMN tenant_id SET DEFAULT '00000000-0000-4000-a000-000000000001';
ALTER TABLE changes ALTER COLUMN tenant_id SET DEFAULT '00000000-0000-4000-a000-000000000001';
ALTER TABLE incidents ALTER COLUMN tenant_id SET DEFAULT '00000000-0000-4000-a000-000000000001';

ALTER TABLE services DROP CONSTRAINT IF EXISTS services_name_key;
CREATE UNIQUE INDEX IF NOT EXISTS idx_services_tenant_name ON services(tenant_id, name);

-- ================================
-- ROW LEVEL SECURITY
-- ================================
ALTER TABLE services ENABLE ROW LEVEL SECURITY;
ALTER TABLE changes ENABLE ROW LEVEL SECURITY;
ALTER TABLE incidents ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation_services ON services;
CREATE POLICY tenant_isolation_services ON services
    USING (
        coalesce(current_setting('app.bypass_rls', true), '') = 'true'
        OR tenant_id = coalesce(
            nullif(current_setting('app.tenant_id', true), '')::uuid,
            '00000000-0000-4000-a000-000000000001'::uuid
        )
    );

DROP POLICY IF EXISTS tenant_isolation_changes ON changes;
CREATE POLICY tenant_isolation_changes ON changes
    USING (
        coalesce(current_setting('app.bypass_rls', true), '') = 'true'
        OR tenant_id = coalesce(
            nullif(current_setting('app.tenant_id', true), '')::uuid,
            '00000000-0000-4000-a000-000000000001'::uuid
        )
    );

DROP POLICY IF EXISTS tenant_isolation_incidents ON incidents;
CREATE POLICY tenant_isolation_incidents ON incidents
    USING (
        coalesce(current_setting('app.bypass_rls', true), '') = 'true'
        OR tenant_id = coalesce(
            nullif(current_setting('app.tenant_id', true), '')::uuid,
            '00000000-0000-4000-a000-000000000001'::uuid
        )
    );

-- ================================
-- SLA TRACKING
-- ================================
CREATE TABLE IF NOT EXISTS sla_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    incident_id UUID NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL CHECK (event_type IN (
        'detected', 'rca_started', 'rca_completed', 'resolved', 'breached'
    )),
    target_minutes INTEGER,
    elapsed_minutes NUMERIC(10, 2),
    breached BOOLEAN NOT NULL DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sla_events_tenant ON sla_events(tenant_id);
CREATE INDEX IF NOT EXISTS idx_sla_events_incident ON sla_events(incident_id);

-- ================================
-- LLM USAGE / COST CONTROLS
-- ================================
CREATE TABLE IF NOT EXISTS llm_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    incident_id UUID REFERENCES incidents(id) ON DELETE SET NULL,
    endpoint TEXT NOT NULL,
    model TEXT,
    prompt_tokens INTEGER NOT NULL DEFAULT 0,
    completion_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER NOT NULL DEFAULT 0,
    estimated_cost_usd NUMERIC(10, 6) DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_llm_usage_tenant_month ON llm_usage(tenant_id, created_at);

-- ================================
-- MODEL DRIFT DETECTION
-- ================================
CREATE TABLE IF NOT EXISTS drift_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    feature_name TEXT NOT NULL,
    mean_value NUMERIC(12, 6),
    std_value NUMERIC(12, 6),
    sample_count INTEGER NOT NULL DEFAULT 0,
    baseline_mean NUMERIC(12, 6),
    baseline_std NUMERIC(12, 6),
    drift_score NUMERIC(8, 4),
    drift_detected BOOLEAN NOT NULL DEFAULT FALSE,
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_drift_tenant ON drift_snapshots(tenant_id, created_at DESC);

-- ================================
-- CANARY SCORING
-- ================================
CREATE TABLE IF NOT EXISTS canary_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    incident_id UUID NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    change_id UUID REFERENCES changes(id) ON DELETE SET NULL,
    production_score NUMERIC(8, 4),
    canary_score NUMERIC(8, 4),
    score_delta NUMERIC(8, 4),
    diverged BOOLEAN NOT NULL DEFAULT FALSE,
    model_version TEXT DEFAULT 'production',
    canary_model_version TEXT DEFAULT 'canary',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_canary_tenant ON canary_predictions(tenant_id, created_at DESC);

-- ================================
-- CHAOS VALIDATION
-- ================================
CREATE TABLE IF NOT EXISTS chaos_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    scenario TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'running', 'passed', 'failed')),
    injected_failure TEXT,
    expected_rca_change_id UUID REFERENCES changes(id) ON DELETE SET NULL,
    actual_top_change_id UUID REFERENCES changes(id) ON DELETE SET NULL,
    rca_accuracy NUMERIC(5, 4),
    duration_ms INTEGER,
    result JSONB DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chaos_tenant ON chaos_runs(tenant_id, created_at DESC);
