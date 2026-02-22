import psycopg2
from datetime import timedelta
from app.reasoning.graph_traversal import get_downstream_services


def build_features_for_incident(db_url: str, incident_id: str):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # 1️⃣ Get incident start time
    cur.execute(
        "SELECT started_at FROM incidents WHERE id = %s",
        (incident_id,),
    )
    row = cur.fetchone()
    if not row:
        raise ValueError("Incident not found")

    incident_start = row[0]

    # 2️⃣ Get directly affected services
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

    # 3️⃣ Expand downstream services (graph reasoning)
    affected_services = get_downstream_services(conn, direct_services)

    # 4️⃣ Candidate changes (24h window BEFORE incident)
    cur.execute(
        """
        SELECT id, created_at
        FROM changes
        WHERE created_at BETWEEN %s AND %s
        """,
        (incident_start - timedelta(hours=24), incident_start),
    )
    changes = cur.fetchall()

    # Idempotency
    cur.execute(
        "DELETE FROM incident_change_features WHERE incident_id = %s",
        (incident_id,),
    )

    for change_id, change_time in changes:

        # ---------- Temporal Proximity ----------
        hours_diff = abs((incident_start - change_time).total_seconds()) / 3600
        temporal_proximity = max(0.0, 1 - (hours_diff / 24))

        # ---------- Service Overlap ----------
        cur.execute(
            """
            SELECT entity_id
            FROM change_impacts
            WHERE change_id = %s
              AND entity_type = 'service'
            """,
            (change_id,),
        )
        impacted_services = {r[0] for r in cur.fetchall()}

        overlap_count = len(impacted_services.intersection(set(affected_services)))
        service_overlap = min(1.0, overlap_count)

        # ---------- Graph Distance ----------
        # 0 if direct overlap, 1 if indirect, 2 if weak
        if overlap_count > 0:
            graph_distance = 0
        elif impacted_services:
            graph_distance = 1
        else:
            graph_distance = 2

        # ---------- Criticality Score ----------
        if impacted_services:
            cur.execute(
                """
                SELECT MAX(
                    CASE criticality
                        WHEN 'high' THEN 1.0
                        WHEN 'medium' THEN 0.6
                        WHEN 'low' THEN 0.3
                        ELSE 0.0
                    END
                )
                FROM services
                WHERE id = ANY(%s::uuid[])
                """,
                (list(impacted_services),),
            )

            criticality_score = cur.fetchone()[0] or 0.0
        else:
            criticality_score = 0.0


        # ---------- Insert Feature Row ----------
        cur.execute(
            """
            INSERT INTO incident_change_features
              (incident_id,
               change_id,
               temporal_proximity,
               service_overlap,
               graph_distance,
               criticality_score,
               label)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                incident_id,
                change_id,
                temporal_proximity,
                service_overlap,
                graph_distance,
                criticality_score,
                0,  # label unknown initially
            ),
        )

    conn.commit()
    cur.close()
    conn.close()