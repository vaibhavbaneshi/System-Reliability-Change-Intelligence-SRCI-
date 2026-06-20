import os

import psycopg2
from fastapi import APIRouter, HTTPException

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL", "")


@router.get("/incidents/{incident_id}/evidence")
def list_evidence(incident_id: str):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("SELECT id FROM incidents WHERE id = %s", (incident_id,))
    if cur.fetchone() is None:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Incident not found")

    cur.execute(
        """
        SELECT id, source_type, reference, created_at
        FROM evidence
        WHERE incident_id = %s
        ORDER BY created_at DESC
        """,
        (incident_id,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return {
        "incident_id": incident_id,
        "evidence": [
            {
                "id": str(r[0]),
                "source_type": r[1],
                "reference": r[2],
                "created_at": r[3].isoformat() if r[3] else None,
            }
            for r in rows
        ],
    }
