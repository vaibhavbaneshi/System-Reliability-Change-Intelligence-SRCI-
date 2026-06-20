-- Indexes, unique constraints, and foreign keys (Phase 14.2)

CREATE INDEX IF NOT EXISTS idx_changes_created_at
    ON changes (created_at);

CREATE INDEX IF NOT EXISTS idx_change_impacts_change_id
    ON change_impacts (change_id);

CREATE INDEX IF NOT EXISTS idx_dependencies_target_id
    ON dependencies (target_id);

CREATE INDEX IF NOT EXISTS idx_incident_entities_incident_id
    ON incident_entities (incident_id);

CREATE INDEX IF NOT EXISTS idx_hypotheses_incident_change
    ON root_cause_hypotheses (incident_id, change_id);

CREATE UNIQUE INDEX IF NOT EXISTS uq_incident_change_features_pair
    ON incident_change_features (incident_id, change_id);

CREATE UNIQUE INDEX IF NOT EXISTS uq_hypotheses_incident_change
    ON root_cause_hypotheses (incident_id, change_id)
    WHERE change_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_change_impacts_entity
    ON change_impacts (change_id, entity_type, entity_id);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_icf_incident'
    ) THEN
        ALTER TABLE incident_change_features
            ADD CONSTRAINT fk_icf_incident
            FOREIGN KEY (incident_id) REFERENCES incidents (id) ON DELETE CASCADE;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_icf_change'
    ) THEN
        ALTER TABLE incident_change_features
            ADD CONSTRAINT fk_icf_change
            FOREIGN KEY (change_id) REFERENCES changes (id) ON DELETE CASCADE;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_hypotheses_change'
    ) THEN
        ALTER TABLE root_cause_hypotheses
            ADD CONSTRAINT fk_hypotheses_change
            FOREIGN KEY (change_id) REFERENCES changes (id) ON DELETE SET NULL;
    END IF;
END $$;
