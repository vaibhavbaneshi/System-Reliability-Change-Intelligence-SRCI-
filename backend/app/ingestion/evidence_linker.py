import psycopg2

def link_change_evidence(db_url: str, incident_id: str):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # Clear old auto-generated evidence
    cur.execute(
        "DELETE FROM evidence WHERE incident_id = %s AND source_type = 'change'",
        (incident_id,),
    )

    # Fetch hypotheses with structured change_id
    cur.execute(
        """
        SELECT change_id
        FROM root_cause_hypotheses
        WHERE incident_id = %s
        """,
        (incident_id,),
    )

    changes = cur.fetchall()

    for (change_id,) in changes:
        # Fetch change metadata
        cur.execute(
            """
            SELECT git_ref, created_at
            FROM changes
            WHERE id = %s
            """,
            (change_id,),
        )
        change_data = cur.fetchone()

        if change_data:
            git_ref, created_at = change_data

            cur.execute(
                """
                INSERT INTO evidence
                  (incident_id, source_type, reference)
                VALUES
                  (%s, 'change', %s)
                """,
                (
                    incident_id,
                    f"Deployment {git_ref} at {created_at}"
                ),
            )

    conn.commit()
    cur.close()
    conn.close()