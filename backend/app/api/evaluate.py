import os

from fastapi import APIRouter, HTTPException

from app.ml.rca_evaluator import evaluate_rca_for_incident

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL", "")


@router.post("/incidents/{incident_id}/evaluate")
def evaluate_incident(incident_id: str):
    try:
        return evaluate_rca_for_incident(DATABASE_URL, incident_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
