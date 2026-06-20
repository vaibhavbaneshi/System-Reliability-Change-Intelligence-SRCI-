-- Phase 15.4 — Advanced Graph Intelligence
-- Recursive CTE graph traversal functions

CREATE OR REPLACE FUNCTION srci_graph_downstream(
    p_seed_ids UUID[],
    p_max_depth INT DEFAULT 10
)
RETURNS TABLE (
    origin_id UUID,
    service_id UUID,
    depth INT,
    dependency_type TEXT
)
LANGUAGE sql
STABLE
AS $$
    WITH RECURSIVE walk AS (
        SELECT
            seed AS origin_id,
            d.source_id AS service_id,
            1 AS depth,
            d.dependency_type,
            ARRAY[d.source_id] AS path
        FROM unnest(p_seed_ids) AS seed
        JOIN dependencies d
          ON d.target_id = seed
         AND d.source_type = 'service'
         AND d.target_type = 'service'

        UNION ALL

        SELECT
            w.origin_id,
            d.source_id,
            w.depth + 1,
            d.dependency_type,
            w.path || d.source_id
        FROM walk w
        JOIN dependencies d
          ON d.target_id = w.service_id
         AND d.source_type = 'service'
         AND d.target_type = 'service'
        WHERE w.depth < p_max_depth
          AND NOT d.source_id = ANY(w.path)
    )
    SELECT DISTINCT origin_id, service_id, depth, dependency_type
    FROM walk
    ORDER BY origin_id, depth, service_id;
$$;

CREATE OR REPLACE FUNCTION srci_graph_upstream(
    p_seed_ids UUID[],
    p_max_depth INT DEFAULT 10
)
RETURNS TABLE (
    origin_id UUID,
    service_id UUID,
    depth INT,
    dependency_type TEXT
)
LANGUAGE sql
STABLE
AS $$
    WITH RECURSIVE walk AS (
        SELECT
            seed AS origin_id,
            d.target_id AS service_id,
            1 AS depth,
            d.dependency_type,
            ARRAY[d.target_id] AS path
        FROM unnest(p_seed_ids) AS seed
        JOIN dependencies d
          ON d.source_id = seed
         AND d.source_type = 'service'
         AND d.target_type = 'service'

        UNION ALL

        SELECT
            w.origin_id,
            d.target_id,
            w.depth + 1,
            d.dependency_type,
            w.path || d.target_id
        FROM walk w
        JOIN dependencies d
          ON d.source_id = w.service_id
         AND d.source_type = 'service'
         AND d.target_type = 'service'
        WHERE w.depth < p_max_depth
          AND NOT d.target_id = ANY(w.path)
    )
    SELECT DISTINCT origin_id, service_id, depth, dependency_type
    FROM walk
    ORDER BY origin_id, depth, service_id;
$$;

CREATE TABLE IF NOT EXISTS change_blast_radius (
    change_id UUID PRIMARY KEY REFERENCES changes(id) ON DELETE CASCADE,
    blast_score NUMERIC(8, 4) NOT NULL DEFAULT 0,
    total_services INT NOT NULL DEFAULT 0,
    max_depth INT NOT NULL DEFAULT 0,
    upstream_count INT NOT NULL DEFAULT 0,
    downstream_count INT NOT NULL DEFAULT 0,
    risk_score NUMERIC(8, 4) NOT NULL DEFAULT 0,
    risk_band TEXT NOT NULL DEFAULT 'low',
    analysis JSONB NOT NULL DEFAULT '{}',
    computed_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_change_blast_radius_computed
    ON change_blast_radius(computed_at DESC);
