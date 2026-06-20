-- Persist RCA summary on incidents for dashboard / weak-rca queue

ALTER TABLE incidents
    ADD COLUMN IF NOT EXISTS auto_rca_hybrid_score FLOAT,
    ADD COLUMN IF NOT EXISTS auto_rca_confidence_band VARCHAR(16),
    ADD COLUMN IF NOT EXISTS auto_rca_should_escalate BOOLEAN,
    ADD COLUMN IF NOT EXISTS auto_rca_quality_score FLOAT,
    ADD COLUMN IF NOT EXISTS auto_rca_quality_band VARCHAR(16);

CREATE INDEX IF NOT EXISTS idx_incidents_weak_rca
    ON incidents (auto_rca_should_escalate)
    WHERE auto_rca_should_escalate = TRUE;
