import psycopg2
from datetime import timedelta

def correlate_incident_to_changes(db_url: str, incident_id: str):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # 1. Incident start time
    cur.execute(
        "SELECT started_at FROM incidents WHERE id = %s",
        (incident_id,),
    )
    result = cur.fetchone()
    if result is None:
        raise ValueError(f"Incident with id {incident_id} not found")
    incident_started_at = result[0]

    # 2. Services affected by incident
    cur.execute(
        """
        SELECT entity_id
        FROM incident_entities
        WHERE incident_id = %s
          AND entity_type = 'service'
        """,
        (incident_id,),
    )
    affected_services = {r[0] for r in cur.fetchall()}

    # 3. Candidate changes (24h window, ingestion-tolerant)
    cur.execute(
        """
        SELECT id
        FROM changes
        WHERE created_at >= %s
        """,
        (incident_started_at - timedelta(hours=24),),
    )
    candidate_changes = [r[0] for r in cur.fetchall()]

    # Idempotency: clear previous hypotheses
    cur.execute(
        "DELETE FROM root_cause_hypotheses WHERE incident_id = %s",
        (incident_id,),
    )

    hypotheses = []

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

        score = 0.0
        for service_id, impact_level in cur.fetchall():
            if service_id not in affected_services:
                continue

            score += {
                "high": 0.7,
                "medium": 0.4,
                "low": 0.2,
            }.get(impact_level, 0)

        if score > 0:
            hypotheses.append((change_id, min(score, 1.0)))

    # 4. Persist hypotheses
    for change_id, confidence in hypotheses:
        cur.execute(
            """
            INSERT INTO root_cause_hypotheses
              (incident_id, description, confidence)
            VALUES
              (%s, %s, %s)
            """,
            (
                incident_id,
                f"Change {change_id} is a likely contributor",
                confidence,
            ),
        )

    conn.commit()
    cur.close()
    conn.close()

    return hypotheses