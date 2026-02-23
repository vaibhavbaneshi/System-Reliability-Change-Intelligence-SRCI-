import psycopg2


def build_incident_context(db_url: str, incident_id: str):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # -----------------------------
    # Incident details
    # -----------------------------
    cur.execute(
        """
        SELECT id, title, severity, started_at
        FROM incidents
        WHERE id = %s
        """,
        (incident_id,),
    )

    incident_row = cur.fetchone()
    if not incident_row:
        cur.close()
        conn.close()
        raise ValueError("Incident not found")

    incident = {
        "id": incident_row[0],
        "title": incident_row[1],
        "severity": incident_row[2],
        "started_at": str(incident_row[3]),
    }

    # -----------------------------
    # Affected services
    # -----------------------------
    cur.execute(
        """
        SELECT s.id, s.name
        FROM incident_entities ie
        JOIN services s ON ie.entity_id = s.id
        WHERE ie.incident_id = %s
          AND ie.entity_type = 'service'
        """,
        (incident_id,),
    )

    services = [{"id": r[0], "name": r[1]} for r in cur.fetchall()]

    # -----------------------------
    # Hybrid candidate data (NEW 🔥)
    # -----------------------------
    cur.execute(
        """
        SELECT
            f.change_id,
            f.temporal_proximity,
            f.service_overlap,
            f.graph_distance,
            f.criticality_score,
            COALESCE(h.confidence, 0) AS rule_confidence
        FROM incident_change_features f
        LEFT JOIN root_cause_hypotheses h
          ON f.incident_id = h.incident_id
         AND f.change_id = h.change_id
        WHERE f.incident_id = %s
        """,
        (incident_id,),
    )

    candidates = []

    for row in cur.fetchall():
        candidates.append(
            {
                "change_id": row[0],
                "temporal_proximity": float(row[1]),
                "service_overlap": float(row[2]),
                "graph_distance": int(row[3]),
                "criticality_score": float(row[4]),
                "rule_confidence": float(row[5]),
            }
        )

    # -----------------------------
    # Evidence
    # -----------------------------
    cur.execute(
        """
        SELECT source_type, reference
        FROM evidence
        WHERE incident_id = %s
        """,
        (incident_id,),
    )

    evidence = [{"type": r[0], "reference": r[1]} for r in cur.fetchall()]

    cur.close()
    conn.close()

    return {
        "incident": incident,
        "affected_services": services,
        "candidates": candidates,  # ⭐ upgraded
        "evidence": evidence,
    }