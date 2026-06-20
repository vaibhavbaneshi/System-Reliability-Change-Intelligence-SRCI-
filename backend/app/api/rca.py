import os

from fastapi import APIRouter, Depends, HTTPException

from app.auth.config import AuthContext
from app.auth.deps import require_auth, require_role
from app.autonomy.rca_runner import (
    RcaCircuitOpenError,
    RcaInProgressError,
    RcaRunnerError,
    run_rca_for_incident,
)
from app.enterprise.sla import get_tenant_sla_target, record_sla_event

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL", "")


@router.post("/incidents/{incident_id}/run-rca")
def run_rca(
    incident_id: str,
    auth: AuthContext = Depends(require_role("admin", "analyst")),
):
    target = get_tenant_sla_target(auth.tenant_id)
    record_sla_event(auth.tenant_id, incident_id, "rca_started", target_minutes=target)
    try:
        result = run_rca_for_incident(DATABASE_URL, incident_id)
        record_sla_event(
            auth.tenant_id, incident_id, "rca_completed", target_minutes=target
        )
        return result
    except RcaInProgressError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except RcaCircuitOpenError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RcaRunnerError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        raise HTTPException(status_code=500, detail=str(exc)) from exc
