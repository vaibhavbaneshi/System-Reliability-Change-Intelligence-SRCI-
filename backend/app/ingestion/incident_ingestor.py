import psycopg2
from typing import List
from datetime import datetime

def ingest_incident(
    db_url: str,
    title: str,
    severity: str,
    started_at: datetime,
    affected_services: List[str],
):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # 1) Insert incident
    cur.execute(
        """
        INSERT INTO incidents (title, severity, started_at)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (title, severity, started_at),
    )
    incident_id = cur.fetchone()[0]

    # 2) Resolve services
    cur.execute(
        "SELECT id, name FROM services WHERE name = ANY(%s)",
        (affected_services,),
    )
    service_rows = cur.fetchall()

    # 3) Link incident to entities
    for service_id, _ in service_rows:
        cur.execute(
            """
            INSERT INTO incident_entities (incident_id, entity_type, entity_id)
            VALUES (%s, 'service', %s)
            """,
            (incident_id, service_id),
        )

    conn.commit()
    cur.close()
    conn.close()

    return incident_id