import psycopg2
from datetime import timedelta
from app.reasoning.graph_traversal import get_downstream_services

def correlate_incident_to_changes(db_url: str, incident_id: str):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # 1️⃣ Fetch incident start time
    cur.execute(
        "SELECT started_at FROM incidents WHERE id = %s",
        (incident_id,),
    )
    result = cur.fetchone()
    if result is None:
        raise ValueError(f"Incident with id {incident_id} not found")

    incident_started_at = result[0]

    # 2️⃣ Fetch affected services
    cur.execute(
        """
        SELECT entity_id
        FROM incident_entities
        WHERE incident_id = %s
          AND entity_type = 'service'
        """,
        (incident_id,),
    )
    direct_services = {r[0] for r in cur.fetchall()}
    affected_services = get_downstream_services(conn, direct_services)

    # 3️⃣ Candidate changes (within 24h before incident)
    cur.execute(
        """
        SELECT id
        FROM changes
        WHERE created_at >= %s
        """,
        (incident_started_at - timedelta(hours=24),),
    )
    candidate_changes = [r[0] for r in cur.fetchall()]

    # Clear previous hypotheses (idempotent)
    cur.execute(
        "DELETE FROM root_cause_hypotheses WHERE incident_id = %s",
        (incident_id,),
    )

    hypotheses = []

    # 4️⃣ Score each candidate change
    for change_id in candidate_changes:

        cur.execute(
            """
            SELECT entity_id, impact_level
            FROM change_impacts
            WHERE change_id = %s
              AND entity_type = 'service'
            """,
            (change_id,),
        )

        rows = cur.fetchall()

        score = 0.0

        for service_id, impact_level in rows:
            if service_id not in affected_services:
                continue

            score += {
                "high": 0.7,
                "medium": 0.4,
                "low": 0.2,
            }.get(impact_level, 0)

        # Only create hypothesis if there is overlap
        if score > 0:

            # 🔹 Evidence-aware boost (per change)
            # Evidence-aware boost (change-specific)
            cur.execute("""
                SELECT COUNT(*)
                FROM evidence
                WHERE incident_id = %s
                AND source_type = 'change'
                AND reference = %s
            """, (incident_id, f"Change {change_id}"))

            evidence_count = cur.fetchone()[0]

            score += min(0.2, evidence_count * 0.1)
            score = min(score, 1.0)

            hypotheses.append((change_id, score))

    # 5️⃣ Persist hypotheses (RELATIONAL, NOT TEXT-PARSED)
    for change_id, confidence in hypotheses:
        cur.execute(
            """
            INSERT INTO root_cause_hypotheses
              (incident_id, change_id, description, confidence)
            VALUES
              (%s, %s, %s, %s)
            """,
            (
                incident_id,
                change_id,
                f"Change {change_id} is a likely contributor",
                confidence,
            ),
        )

    conn.commit()
    cur.close()
    conn.close()

    return hypotheses