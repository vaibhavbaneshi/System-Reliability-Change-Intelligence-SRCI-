import psycopg2
from datetime import datetime
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

    # 3️⃣ Get expanded downstream services
    affected_services = get_downstream_services(conn, direct_services)

    # 4️⃣ Candidate changes (24h window)
    cur.execute(
        """
        SELECT id, created_at
        FROM changes
        WHERE created_at >= %s
        """,
        (incident_start,),
    )
    changes = cur.fetchall()

    # Clear previous features (idempotent)
    cur.execute(
        "DELETE FROM incident_change_features WHERE incident_id = %s",
        (incident_id,),
    )

    for change_id, change_time in changes:

        # Impact score
        cur.execute(
            """
            SELECT impact_level
            FROM change_impacts
            WHERE change_id = %s
              AND entity_type = 'service'
            """,
            (change_id,),
        )

        impact_score = 0.0
        graph_distance = 3  # default large

        rows = cur.fetchall()
        for (impact_level,) in rows:
            impact_score += {
                "high": 0.7,
                "medium": 0.4,
                "low": 0.2,
            }.get(impact_level, 0)

        impact_score = min(impact_score, 1.0)

        # Time delta (hours)
        time_delta = abs((incident_start - change_time).total_seconds()) / 3600

        # Evidence count
        cur.execute(
            """
            SELECT COUNT(*)
            FROM evidence
            WHERE incident_id = %s
              AND reference ILIKE %s
            """,
            (incident_id, f"%{change_id}%"),
        )
        evidence_count = cur.fetchone()[0]

        # Insert feature row
        cur.execute(
            """
            INSERT INTO incident_change_features
              (incident_id, change_id, impact_score,
               graph_distance, time_delta_hours,
               evidence_count, label)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                incident_id,
                change_id,
                impact_score,
                graph_distance,
                time_delta,
                evidence_count,
                0,  # label unknown
            ),
        )

    conn.commit()
    cur.close()
    conn.close()