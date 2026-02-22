DROP TABLE IF EXISTS incident_change_features;

CREATE TABLE incident_change_features (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id UUID,
    change_id UUID,
    temporal_proximity FLOAT,
    service_overlap FLOAT,
    graph_distance FLOAT,
    criticality_score FLOAT,
    label INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);