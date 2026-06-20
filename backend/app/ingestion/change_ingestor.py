from __future__ import annotations

from typing import List

from app.db import get_connection
from app.tenant.context import get_current_tenant_id


def ingest_change(
    db_url: str,
    change_type: str,
    description: str,
    git_ref: str,
    services_touched: List[str],
    tenant_id: str | None = None,
):
    tid = tenant_id or get_current_tenant_id()
    conn = get_connection(tenant_id=tid)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO changes (change_type, description, git_ref, tenant_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (change_type, description, git_ref, tid),
    )
    change_id = cur.fetchone()[0]

    cur.execute(
        """
        SELECT id, name
        FROM services
        WHERE name = ANY(%s)
        """,
        (services_touched,),
    )
    service_rows = cur.fetchall()

    for service_id, _ in service_rows:
        cur.execute(
            """
            INSERT INTO change_impacts (change_id, entity_type, entity_id, impact_level)
            VALUES (%s, 'service', %s, 'high')
            """,
            (change_id, service_id),
        )

    conn.commit()
    cur.close()
    conn.close()

    return change_id
