from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from pydantic import BaseModel

from app.auth.config import AuthContext
from app.auth.deps import require_auth, require_role
from app.enterprise.sla import get_sla_summary, get_tenant_sla_target, record_sla_event

router = APIRouter(prefix="/sla", tags=["sla"])


class SlaEventRequest(BaseModel):
    incident_id: str
    event_type: str
    metadata: Optional[dict] = None


@router.get("/summary")
def sla_summary(days: int = 30, auth: AuthContext = Depends(require_auth)):
    return get_sla_summary(auth.tenant_id, days=days)


@router.get("/target")
def sla_target(auth: AuthContext = Depends(require_auth)):
    return {"target_minutes": get_tenant_sla_target(auth.tenant_id)}


@router.post("/events")
def create_sla_event(
    req: SlaEventRequest,
    auth: AuthContext = Depends(require_role("admin", "analyst")),
):
    allowed = {"detected", "rca_started", "rca_completed", "resolved", "breached"}
    if req.event_type not in allowed:
        raise HTTPException(status_code=400, detail=f"event_type must be one of {allowed}")

    target = get_tenant_sla_target(auth.tenant_id)
    return record_sla_event(
        auth.tenant_id,
        req.incident_id,
        req.event_type,
        target_minutes=target,
        metadata=req.metadata,
    )
