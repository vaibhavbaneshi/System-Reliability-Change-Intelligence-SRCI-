-- Track whether services came from demo seed or Git import
ALTER TABLE services ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'demo';
ALTER TABLE services ADD COLUMN IF NOT EXISTS git_yaml_path TEXT;
ALTER TABLE services ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

ALTER TABLE git_connections ADD COLUMN IF NOT EXISTS last_service_paths JSONB DEFAULT '[]'::jsonb;

CREATE INDEX IF NOT EXISTS idx_services_source ON services(tenant_id, source);
