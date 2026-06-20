import os

from fastapi import APIRouter, Depends, HTTPException

from app.auth.config import AuthContext
from app.auth.deps import require_auth
from app.db import get_connection

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL", "")


def _serialize_incident_row(row) -> dict:
    return {
        "id": str(row[0]),
        "title": row[1],
        "severity": row[2],
        "started_at": row[3].isoformat() if row[3] else None,
        "auto_rca_processed": bool(row[4]),
        "auto_rca_processed_at": row[5].isoformat() if row[5] else None,
        "auto_rca_attempts": row[6] or 0,
        "auto_rca_in_progress": bool(row[7]),
        "auto_rca_hybrid_score": float(row[8]) if row[8] is not None else None,
        "auto_rca_confidence_band": row[9],
        "auto_rca_should_escalate": bool(row[10]) if row[10] is not None else None,
        "auto_rca_quality_score": float(row[11]) if row[11] is not None else None,
        "auto_rca_quality_band": row[12],
    }


_INCIDENT_SELECT = """
    SELECT id, title, severity, started_at,
           auto_rca_processed, auto_rca_processed_at, auto_rca_attempts,
           auto_rca_in_progress,
           auto_rca_hybrid_score, auto_rca_confidence_band,
           auto_rca_should_escalate, auto_rca_quality_score, auto_rca_quality_band
    FROM incidents
"""


@router.get("/incidents")
def list_incidents(auth: AuthContext = Depends(require_auth)):
    conn = get_connection(tenant_id=auth.tenant_id)
    cur = conn.cursor()
    cur.execute(f"{_INCIDENT_SELECT} ORDER BY started_at DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"incidents": [_serialize_incident_row(r) for r in rows]}


@router.get("/incidents/weak-rca")
def list_weak_rca_incidents(auth: AuthContext = Depends(require_auth)):
    conn = get_connection(tenant_id=auth.tenant_id)
    cur = conn.cursor()
    cur.execute(
        f"""
        {_INCIDENT_SELECT}
        WHERE auto_rca_should_escalate = TRUE
        ORDER BY started_at DESC
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"incidents": [_serialize_incident_row(r) for r in rows]}


@router.get("/incidents/{incident_id}")
def get_incident(incident_id: str, auth: AuthContext = Depends(require_auth)):
    conn = get_connection(tenant_id=auth.tenant_id)
    cur = conn.cursor()
    cur.execute(f"{_INCIDENT_SELECT} WHERE id = %s", (incident_id,))
    row = cur.fetchone()
    if row is None:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Incident not found")

    cur.execute(
        """
        SELECT s.id, s.name, s.criticality
        FROM incident_entities ie
        JOIN services s ON ie.entity_id = s.id
        WHERE ie.incident_id = %s AND ie.entity_type = 'service'
        """,
        (incident_id,),
    )
    services = [
        {"id": str(r[0]), "name": r[1], "criticality": r[2]} for r in cur.fetchall()
    ]
    cur.close()
    conn.close()

    incident = _serialize_incident_row(row)
    incident["affected_services"] = services
    return incident
