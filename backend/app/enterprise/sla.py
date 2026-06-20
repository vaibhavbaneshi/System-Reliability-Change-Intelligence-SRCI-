from __future__ import annotations

from datetime import datetime, timezone

from app.db import get_connection


def record_sla_event(
    tenant_id: str,
    incident_id: str,
    event_type: str,
    target_minutes: int | None = None,
    metadata: dict | None = None,
) -> dict:
    conn = get_connection(tenant_id=tenant_id)
    cur = conn.cursor()

    elapsed = None
    breached = False
    if event_type in ("rca_completed", "resolved", "breached"):
        cur.execute(
            "SELECT started_at FROM incidents WHERE id = %s",
            (incident_id,),
        )
        row = cur.fetchone()
        if row and row[0]:
            started = row[0]
            if started.tzinfo is None:
                started = started.replace(tzinfo=timezone.utc)
            elapsed = (datetime.now(timezone.utc) - started).total_seconds() / 60.0
            if target_minutes and elapsed > target_minutes:
                breached = True

    cur.execute(
        """
        INSERT INTO sla_events
            (tenant_id, incident_id, event_type, target_minutes, elapsed_minutes, breached, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
        RETURNING id, event_type, elapsed_minutes, breached, created_at
        """,
        (
            tenant_id,
            incident_id,
            event_type,
            target_minutes,
            elapsed,
            breached,
            __import__("json").dumps(metadata or {}),
        ),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return {
        "id": str(row[0]),
        "event_type": row[1],
        "elapsed_minutes": float(row[2]) if row[2] is not None else None,
        "breached": row[3],
        "created_at": row[4].isoformat(),
    }


def get_sla_summary(tenant_id: str, days: int = 30) -> dict:
    conn = get_connection(tenant_id=tenant_id)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            COUNT(*) FILTER (WHERE event_type = 'rca_completed') AS rca_completed,
            COUNT(*) FILTER (WHERE breached = TRUE) AS breaches,
            AVG(elapsed_minutes) FILTER (WHERE event_type = 'rca_completed') AS avg_rca_minutes,
            AVG(target_minutes) AS avg_target
        FROM sla_events
        WHERE tenant_id = %s
          AND created_at >= NOW() - (%s || ' days')::interval
        """,
        (tenant_id, days),
    )
    row = cur.fetchone()
    cur.execute(
        """
        SELECT event_type, incident_id, elapsed_minutes, breached, created_at
        FROM sla_events
        WHERE tenant_id = %s
        ORDER BY created_at DESC
        LIMIT 20
        """,
        (tenant_id,),
    )
    recent = [
        {
            "event_type": r[0],
            "incident_id": str(r[1]),
            "elapsed_minutes": float(r[2]) if r[2] is not None else None,
            "breached": r[3],
            "created_at": r[4].isoformat(),
        }
        for r in cur.fetchall()
    ]
    cur.close()
    conn.close()

    completed = row[0] or 0
    breaches = row[1] or 0
    compliance = 1.0 - (breaches / completed) if completed else 1.0

    return {
        "period_days": days,
        "rca_completed": completed,
        "breaches": breaches,
        "compliance_rate": round(compliance, 4),
        "avg_rca_minutes": round(float(row[2]), 2) if row[2] else None,
        "avg_target_minutes": round(float(row[3]), 2) if row[3] else None,
        "recent_events": recent,
    }


def get_tenant_sla_target(tenant_id: str) -> int:
    conn = get_connection(bypass_rls=True)
    cur = conn.cursor()
    cur.execute("SELECT sla_target_minutes FROM tenants WHERE id = %s", (tenant_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row and row[0] else 60
