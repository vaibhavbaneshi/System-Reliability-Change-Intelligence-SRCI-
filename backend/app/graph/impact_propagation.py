from __future__ import annotations

from app.config.settings import dependency_weight, DEPTH_DECAY
from app.db import get_connection
from app.reasoning.graph_traversal import traverse_downstream_with_depth


def propagate_change_impact_weighted(db_url: str, change_id: str) -> dict:
    """
    Propagate change impact using dependency_type weights and depth decay.
    Replaces flat medium/low assignment with weighted probabilities.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT entity_id
        FROM change_impacts
        WHERE change_id = %s
          AND entity_type = 'service'
          AND impact_level = 'high'
        """,
        (change_id,),
    )
    starting_services = [row[0] for row in cur.fetchall()]

    if not starting_services:
        cur.close()
        conn.close()
        return {"propagated": 0, "change_id": change_id}

    cur.execute(
        """
        SELECT source_id, target_id, dependency_type
        FROM dependencies
        WHERE source_type = 'service' AND target_type = 'service'
        """
    )
    edge_weights = {}
    for source_id, target_id, dep_type in cur.fetchall():
        edge_weights[(source_id, target_id)] = dependency_weight(dep_type)

    depths = traverse_downstream_with_depth(conn, starting_services, dependency_types=None)

    inserted = 0
    for service_id, depth in depths.items():
        if depth == 0:
            continue

        propagation = DEPTH_DECAY ** depth
        impact = "high" if propagation >= 0.75 else "medium" if propagation >= 0.45 else "low"

        cur.execute(
            """
            INSERT INTO change_impacts (change_id, entity_type, entity_id, impact_level)
            VALUES (%s, 'service', %s, %s)
            ON CONFLICT (change_id, entity_type, entity_id) DO NOTHING
            """,
            (change_id, service_id, impact),
        )
        if cur.rowcount:
            inserted += 1

    conn.commit()
    cur.close()
    conn.close()

    from app.graph.blast_radius import compute_blast_radius

    blast = compute_blast_radius(change_id, persist=True)
    return {
        "propagated": inserted,
        "change_id": change_id,
        "blast_radius": blast["blast_radius"],
        "risk_panel": blast["risk_panel"],
    }
