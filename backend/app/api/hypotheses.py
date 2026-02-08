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
                "hypothesis_id": r[0],
                "description": r[1],
                "confidence": r[2],
                "created_at": r[3],
            }
            for r in rows
        ],
    }