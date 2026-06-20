import os
from typing import Optional

import psycopg2
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.autonomy.learning_loop import apply_confirmed_feedback, maybe_retrain
from app.autonomy.monitor import get_monitor

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL", "")

VALID_VERDICTS = {"confirmed", "rejected", "corrected"}


class FeedbackRequest(BaseModel):
    verdict: str = Field(..., description="confirmed | rejected | corrected")
    change_id: Optional[str] = None
    comment: Optional[str] = None


@router.post("/incidents/{incident_id}/feedback")
def submit_feedback(incident_id: str, body: FeedbackRequest):
    if body.verdict not in VALID_VERDICTS:
        raise HTTPException(
            status_code=400,
            detail=f"verdict must be one of {sorted(VALID_VERDICTS)}",
        )

    if body.verdict in ("confirmed", "corrected") and not body.change_id:
        raise HTTPException(
            status_code=400,
            detail="change_id required for confirmed/corrected verdicts",
        )

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT id FROM incidents WHERE id = %s", (incident_id,))
    if cur.fetchone() is None:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    cur.execute(
        """
        INSERT INTO rca_feedback (incident_id, change_id, verdict, comment)
        VALUES (%s, %s, %s, %s)
        RETURNING id, created_at
        """,
        (incident_id, body.change_id, body.verdict, body.comment),
    )
    feedback_id, created_at = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    learning_result = None
    if body.verdict in ("confirmed", "corrected"):
        learning_result = apply_confirmed_feedback(
            DATABASE_URL, incident_id, body.change_id
        )
    elif body.verdict == "rejected":
        learning_result = {"retrain": maybe_retrain(DATABASE_URL)}

    return {
        "feedback_id": str(feedback_id),
        "incident_id": incident_id,
        "verdict": body.verdict,
        "change_id": body.change_id,
        "created_at": created_at.isoformat(),
        "learning": learning_result,
    }


@router.get("/incidents/{incident_id}/feedback")
def list_feedback(incident_id: str):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, change_id, verdict, comment, created_at
        FROM rca_feedback
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
        "feedback": [
            {
                "feedback_id": str(r[0]),
                "change_id": str(r[1]) if r[1] else None,
                "verdict": r[2],
                "comment": r[3],
                "created_at": r[4].isoformat() if r[4] else None,
            }
            for r in rows
        ],
    }
