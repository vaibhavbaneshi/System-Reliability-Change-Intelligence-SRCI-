import psycopg2

def build_incident_context(db_url: str, incident_id: str):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # 1️⃣ Incident details
    cur.execute(
        """
        SELECT title, severity, started_at
        FROM incidents
        WHERE id = %s
        """,
        (incident_id,),
    )
    incident = cur.fetchone()
    if incident is None:
        raise ValueError("Incident not found")

    title, severity, started_at = incident

    # 2️⃣ Affected services
    cur.execute(
        """
        SELECT s.id, s.name
        FROM services s
        JOIN incident_entities ie
          ON s.id = ie.entity_id
        WHERE ie.incident_id = %s
          AND ie.entity_type = 'service'
        """,
        (incident_id,),
    )
    affected_services = [
        {"id": row[0], "name": row[1]}
        for row in cur.fetchall()
    ]

    # 3️⃣ Root cause hypotheses
    cur.execute(
        """
        SELECT change_id, description, confidence
        FROM root_cause_hypotheses
        WHERE incident_id = %s
        ORDER BY confidence DESC
        """,
        (incident_id,),
    )
    hypotheses = [
        {
            "change_id": row[0],
            "description": row[1],
            "confidence": float(row[2]),
        }
        for row in cur.fetchall()
    ]

    # 4️⃣ Linked evidence
    cur.execute(
        """
        SELECT source_type, reference
        FROM evidence
        WHERE incident_id = %s
        """,
        (incident_id,),
    )
    evidence = [
        {"source_type": row[0], "reference": row[1]}
        for row in cur.fetchall()
    ]

    cur.close()
    conn.close()

    return {
        "incident": {
            "id": incident_id,
            "title": title,
            "severity": severity,
            "started_at": str(started_at),
        },
        "affected_services": affected_services,
        "hypotheses": hypotheses,
        "evidence": evidence,
    }