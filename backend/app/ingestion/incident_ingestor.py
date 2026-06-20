from __future__ import annotations

from datetime import datetime
from typing import List

from app.db import get_connection
from app.tenant.context import get_current_tenant_id


def ingest_incident(
    db_url: str,
    title: str,
    severity: str,
    started_at: datetime,
    affected_services: List[str],
    tenant_id: str | None = None,
):
    tid = tenant_id or get_current_tenant_id()
    conn = get_connection(tenant_id=tid)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO incidents (title, severity, started_at, tenant_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (title, severity, started_at, tid),
    )
    incident_id = cur.fetchone()[0]

    cur.execute(
        "SELECT id, name FROM services WHERE name = ANY(%s)",
        (affected_services,),
    )
    service_rows = cur.fetchall()

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
