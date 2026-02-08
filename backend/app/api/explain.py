import os
import psycopg2
from fastapi import APIRouter
from app.genai.explainer import generate_explanation
from fastapi import HTTPException

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL")

@router.get("/incidents/{incident_id}/explanation")
def explain_incident(incident_id: str):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Incident
    cur.execute(
        """
        SELECT title, severity, started_at
        FROM incidents
        WHERE id = %s
        """,
        (incident_id,),
    )

    incident = cur.fetchone()

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail=f"Incident {incident_id} not found"
        )

    # Hypotheses
    cur.execute(
        """
        SELECT description, confidence
        FROM root_cause_hypotheses
        WHERE incident_id = %s
        ORDER BY confidence DESC
        """,
        (incident_id,),
    )
    hypotheses = cur.fetchall()

    # Evidence
    cur.execute(
        """
        SELECT source_type, reference
        FROM evidence
        WHERE incident_id = %s
        """,
        (incident_id,),
    )
    evidence = cur.fetchall()

    cur.close()
    conn.close()

    context = {
        "incident": {
            "title": incident[0],
            "severity": incident[1],
            "started_at": incident[2].isoformat(),
        },
        "hypotheses": [
            {"description": h[0], "confidence": h[1]} for h in hypotheses
        ],
        "evidence": [
            {"type": e[0], "reference": e[1]} for e in evidence
        ],
    }

    explanation = generate_explanation(context)

    return {
        "incident_id": incident_id,
        "explanation": explanation,
        "confidence": hypotheses[0][1] if hypotheses else None,
    }