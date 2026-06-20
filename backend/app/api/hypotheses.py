import os
import psycopg2
from fastapi import APIRouter

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL")

@router.get("/incidents/{incident_id}/hypotheses")
def get_hypotheses_for_incident(incident_id: str):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            id,
            change_id,
            description,
            confidence,
            created_at
        FROM root_cause_hypotheses
        WHERE incident_id = %s
        ORDER BY confidence DESC
        """,
        (incident_id,),
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "incident_id": incident_id,
        "hypotheses": [
            {
                "hypothesis_id": str(r[0]),
                "change_id": str(r[1]) if r[1] else None,
                "description": r[2],
                "confidence": float(r[3]) if r[3] is not None else 0.0,
                "created_at": r[4].isoformat() if r[4] else None,
            }
            for r in rows
        ],
    }