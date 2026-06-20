-- Phase 18 — Git integration (plug-and-play from UI)

ALTER TABLE changes ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'manual';
ALTER TABLE changes ADD COLUMN IF NOT EXISTS commit_sha TEXT;
ALTER TABLE changes ADD COLUMN IF NOT EXISTS pr_number INTEGER;
ALTER TABLE changes ADD COLUMN IF NOT EXISTS git_connection_id UUID;

CREATE INDEX IF NOT EXISTS idx_changes_source ON changes(source, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_changes_commit_sha ON changes(commit_sha) WHERE commit_sha IS NOT NULL;

CREATE TABLE IF NOT EXISTS git_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    provider TEXT NOT NULL DEFAULT 'github',
    owner TEXT NOT NULL,
    repo TEXT NOT NULL,
    default_branch TEXT NOT NULL DEFAULT 'main',
    access_token TEXT NOT NULL,
    webhook_secret TEXT,
    auto_sync BOOLEAN NOT NULL DEFAULT TRUE,
    ingest_services_from_repo BOOLEAN NOT NULL DEFAULT TRUE,
    last_sync_at TIMESTAMP,
    last_sync_status TEXT,
    last_sync_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, owner, repo)
);

CREATE INDEX IF NOT EXISTS idx_git_connections_tenant ON git_connections(tenant_id);

CREATE TABLE IF NOT EXISTS git_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    connection_id UUID NOT NULL REFERENCES git_connections(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL CHECK (event_type IN ('push', 'pull_request', 'sync', 'manual_sync')),
    git_ref TEXT,
    pr_number INTEGER,
    commit_message TEXT,
    author TEXT,
    services_touched TEXT[],
    change_id UUID REFERENCES changes(id) ON DELETE SET NULL,
    payload JSONB DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_git_events_connection_ref
    ON git_events(connection_id, git_ref)
    WHERE git_ref IS NOT NULL;

CREATE TABLE IF NOT EXISTS pull_request_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    connection_id UUID NOT NULL REFERENCES git_connections(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    pr_number INTEGER NOT NULL,
    title TEXT,
    head_sha TEXT,
    base_branch TEXT,
    state TEXT NOT NULL DEFAULT 'open',
    risk_band TEXT,
    risk_score NUMERIC(8, 4),
    blast_radius JSONB DEFAULT '{}',
    merge_recommendation TEXT,
    services_touched TEXT[],
    change_id UUID REFERENCES changes(id) ON DELETE SET NULL,
    html_url TEXT,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (connection_id, pr_number)
);

CREATE INDEX IF NOT EXISTS idx_pr_checks_tenant ON pull_request_checks(tenant_id, updated_at DESC);
