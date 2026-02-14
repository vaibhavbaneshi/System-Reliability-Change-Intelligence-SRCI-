-- ================================
-- SRCI Initial Schema (v1)
-- ================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ================================
-- SERVICES
-- ================================
CREATE TABLE IF NOT EXISTS services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    owner_team TEXT,
    criticality TEXT CHECK (criticality IN ('low', 'medium', 'high')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ================================
-- APIs (optional but future-safe)
-- ================================
CREATE TABLE IF NOT EXISTS apis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_id UUID REFERENCES services(id) ON DELETE CASCADE,
    path TEXT NOT NULL,
    method TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ================================
-- DATABASE TABLE METADATA
-- ================================
CREATE TABLE IF NOT EXISTS db_tables (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    schema_name TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ================================
-- DEPENDENCIES (GRAPH CORE)
-- ================================
CREATE TABLE IF NOT EXISTS dependencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_type TEXT CHECK (source_type IN ('service', 'api')),
    source_id UUID NOT NULL,
    target_type TEXT CHECK (target_type IN ('service', 'db_table')),
    target_id UUID NOT NULL,
    dependency_type TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ================================
-- CHANGES (PRS / COMMITS / SCHEMA)
-- ================================
CREATE TABLE IF NOT EXISTS changes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    change_type TEXT CHECK (change_type IN ('code', 'schema', 'config')),
    description TEXT,
    git_ref TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by TEXT,
    modified_at TIMESTAMP,
    modified_by TEXT
);

-- ================================
-- CHANGE IMPACTS
-- ================================
CREATE TABLE IF NOT EXISTS change_impacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    change_id UUID REFERENCES changes(id) ON DELETE CASCADE,
    entity_type TEXT CHECK (entity_type IN ('service', 'api', 'db_table')),
    entity_id UUID NOT NULL,
    impact_level TEXT CHECK (impact_level IN ('low', 'medium', 'high')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ================================
-- INCIDENTS
-- ================================
CREATE TABLE IF NOT EXISTS incidents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    severity TEXT CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    started_at TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by TEXT,
    modified_at TIMESTAMP,
    modified_by TEXT
);

-- ================================
-- INCIDENT AFFECTED ENTITIES
-- ================================
CREATE TABLE IF NOT EXISTS incident_entities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id UUID REFERENCES incidents(id) ON DELETE CASCADE,
    entity_type TEXT CHECK (entity_type IN ('service', 'api', 'db_table')),
    entity_id UUID NOT NULL
);

-- ================================
-- ROOT CAUSE HYPOTHESES
-- ================================
CREATE TABLE IF NOT EXISTS root_cause_hypotheses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id UUID REFERENCES incidents(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by TEXT,
    modified_at TIMESTAMP,
    modified_by TEXT
);

-- ================================
-- EVIDENCE
-- ================================
CREATE TABLE IF NOT EXISTS evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id UUID REFERENCES incidents(id) ON DELETE CASCADE,
    source_type TEXT CHECK (source_type IN ('log', 'metric', 'trace', 'change')),
    reference TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by TEXT
);

ALTER TABLE root_cause_hypotheses
ADD COLUMN change_id UUID;