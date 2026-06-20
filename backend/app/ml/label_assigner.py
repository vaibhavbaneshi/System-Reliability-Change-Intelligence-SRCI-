import psycopg2


def assign_labels_for_incident(db_url: str, incident_id: str, labels: list) -> dict:
    """
    Set ground-truth labels on incident_change_features rows.
    Each label entry: {"change_id": "<uuid>", "label": 0|1}
    """
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    cur.execute("SELECT id FROM incidents WHERE id = %s", (incident_id,))
    if cur.fetchone() is None:
        cur.close()
        conn.close()
        raise ValueError(f"Incident {incident_id} not found")

    updated = []
    skipped = []

    for entry in labels:
        change_id = entry["change_id"]
        label = int(entry["label"])
        if label not in (0, 1):
            skipped.append({"change_id": change_id, "reason": "label must be 0 or 1"})
            continue

        cur.execute(
            """
            UPDATE incident_change_features
            SET label = %s
            WHERE incident_id = %s AND change_id = %s
            RETURNING change_id
            """,
            (label, incident_id, change_id),
        )
        row = cur.fetchone()
        if row:
            updated.append({"change_id": change_id, "label": label})
        else:
            skipped.append(
                {
                    "change_id": change_id,
                    "reason": "no feature row for incident/change pair",
                }
            )

    conn.commit()
    cur.close()
    conn.close()

    return {
        "incident_id": incident_id,
        "updated": updated,
        "skipped": skipped,
        "updated_count": len(updated),
    }
