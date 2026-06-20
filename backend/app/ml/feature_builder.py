import psycopg2
from collections import defaultdict
from datetime import timedelta

from app.config.scoring_weights import CRITICALITY_WEIGHTS, TEMPORAL_WINDOW_HOURS
from app.reasoning.graph_traversal import get_downstream_services


def build_features_for_incident(db_url: str, incident_id: str):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    cur.execute(
        "SELECT started_at FROM incidents WHERE id = %s",
        (incident_id,),
    )
    row = cur.fetchone()
    if not row:
        raise ValueError("Incident not found")

    incident_start = row[0]

    cur.execute(
        """
        SELECT entity_id
        FROM incident_entities
        WHERE incident_id = %s
          AND entity_type = 'service'
        """,
        (incident_id,),
    )
    direct_services = [r[0] for r in cur.fetchall()]
    affected_services = get_downstream_services(conn, direct_services)

    cur.execute(
        """
        SELECT id, created_at
        FROM changes
        WHERE created_at BETWEEN %s AND %s
        """,
        (
            incident_start - timedelta(hours=TEMPORAL_WINDOW_HOURS),
            incident_start,
        ),
    )
    changes = cur.fetchall()

    cur.execute(
        "DELETE FROM incident_change_features WHERE incident_id = %s",
        (incident_id,),
    )

    if not changes:
        conn.commit()
        cur.close()
        conn.close()
        return

    change_ids = [c[0] for c in changes]

    cur.execute(
        """
        SELECT change_id, entity_id
        FROM change_impacts
        WHERE change_id = ANY(%s::uuid[])
          AND entity_type = 'service'
        """,
        (change_ids,),
    )
    impacts_by_change = defaultdict(set)
    all_service_ids = set()
    for change_id, entity_id in cur.fetchall():
        impacts_by_change[change_id].add(entity_id)
        all_service_ids.add(entity_id)

    criticality_map = {}
    if all_service_ids:
        cur.execute(
            """
            SELECT id, criticality
            FROM services
            WHERE id = ANY(%s::uuid[])
            """,
            (list(all_service_ids),),
        )
        for sid, crit in cur.fetchall():
            criticality_map[sid] = CRITICALITY_WEIGHTS.get(crit, 0.0)

    rows_to_insert = []
    affected_set = set(affected_services)

    for change_id, change_time in changes:
        hours_diff = abs((incident_start - change_time).total_seconds()) / 3600
        temporal_proximity = max(
            0.0, 1 - (hours_diff / TEMPORAL_WINDOW_HOURS)
        )

        impacted_services = impacts_by_change.get(change_id, set())
        overlap_count = len(impacted_services.intersection(affected_set))
        service_overlap = min(1.0, overlap_count)

        if overlap_count > 0:
            graph_distance = 0
        elif impacted_services:
            graph_distance = 1
        else:
            graph_distance = 2

        if impacted_services:
            criticality_score = max(
                (criticality_map.get(sid, 0.0) for sid in impacted_services),
                default=0.0,
            )
        else:
            criticality_score = 0.0

        rows_to_insert.append(
            (
                incident_id,
                change_id,
                temporal_proximity,
                service_overlap,
                graph_distance,
                criticality_score,
                0,
            )
        )

    if rows_to_insert:
        cur.executemany(
            """
            INSERT INTO incident_change_features
              (incident_id, change_id, temporal_proximity,
               service_overlap, graph_distance, criticality_score, label)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            rows_to_insert,
        )

    conn.commit()
    cur.close()
    conn.close()
