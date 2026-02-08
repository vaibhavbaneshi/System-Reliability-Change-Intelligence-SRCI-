import psycopg2

def link_change_evidence(db_url: str, incident_id: str):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # Get hypotheses
    cur.execute(
        """
        SELECT id, description
        FROM root_cause_hypotheses
        WHERE incident_id = %s
        """,
        (incident_id,),
    )
    hypotheses = cur.fetchall()

    # Clear old evidence (idempotent)
    cur.execute(
        "DELETE FROM evidence WHERE incident_id = %s AND source_type = 'change'",
        (incident_id,),
    )

    for hypothesis_id, description in hypotheses:
        # Extract change id from description (v1 approach)
        change_id = description.split(" ")[1]

        cur.execute(
            """
            INSERT INTO evidence
              (incident_id, source_type, reference)
            VALUES
              (%s, 'change', %s)
            """,
            (incident_id, f"Change {change_id}"),
        )

    conn.commit()
    cur.close()
    conn.close()