CREATE TABLE IF NOT EXISTS incident_change_features (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id UUID NOT NULL,
    change_id UUID NOT NULL,

    impact_score FLOAT,
    graph_distance INT,
    time_delta_hours FLOAT,
    evidence_count INT,

    label INT,

    created_at TIMESTAMP DEFAULT NOW()
);