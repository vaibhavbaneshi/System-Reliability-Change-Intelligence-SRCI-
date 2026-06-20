import os

from fastapi import APIRouter, HTTPException

from app.reasoning.failure_analysis import analyze_rca_failure

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL", "")


@router.get("/incidents/{incident_id}/rca-failure")
def get_rca_failure(incident_id: str):
    try:
        return analyze_rca_failure(DATABASE_URL, incident_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
