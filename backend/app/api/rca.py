import os

from fastapi import APIRouter, HTTPException

from app.autonomy.rca_runner import (
    RcaCircuitOpenError,
    RcaInProgressError,
    RcaRunnerError,
    run_rca_for_incident,
)

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL", "")


@router.post("/incidents/{incident_id}/run-rca")
def run_rca(incident_id: str):
    try:
        return run_rca_for_incident(DATABASE_URL, incident_id)
    except RcaInProgressError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except RcaCircuitOpenError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RcaRunnerError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        raise HTTPException(status_code=500, detail=str(exc)) from exc
