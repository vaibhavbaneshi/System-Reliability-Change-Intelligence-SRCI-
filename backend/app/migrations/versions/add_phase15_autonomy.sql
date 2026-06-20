-- Phase 15: feedback storage + distributed lock timestamp

ALTER TABLE incidents
    ADD COLUMN IF NOT EXISTS auto_rca_locked_at TIMESTAMP;

CREATE TABLE IF NOT EXISTS rca_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id UUID NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    change_id UUID,
    verdict VARCHAR(32) NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rca_feedback_incident
    ON rca_feedback (incident_id);
