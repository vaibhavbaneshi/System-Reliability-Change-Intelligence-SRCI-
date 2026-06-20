-- Autonomy tracking columns on incidents (Phase 14.5)

ALTER TABLE incidents
    ADD COLUMN IF NOT EXISTS auto_rca_processed BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS auto_rca_processed_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS auto_rca_attempts INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS auto_rca_last_error TEXT,
    ADD COLUMN IF NOT EXISTS auto_rca_in_progress BOOLEAN NOT NULL DEFAULT FALSE;
