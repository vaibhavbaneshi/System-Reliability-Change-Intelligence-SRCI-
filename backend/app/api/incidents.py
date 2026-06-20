import os
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List

from app.auth.config import AuthContext
from app.auth.deps import require_role
from app.ingestion.incident_ingestor import ingest_incident
from app.autonomy.event_handler import trigger_rca_on_ingest
from app.enterprise.sla import get_tenant_sla_target, record_sla_event

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL")


class IncidentRequest(BaseModel):
    title: str
    severity: str
    started_at: datetime
    affected_services: List[str]


@router.post("/incidents/ingest")
def ingest_incident_api(
    req: IncidentRequest,
    auth: AuthContext = Depends(require_role("admin", "analyst")),
):
    incident_id = ingest_incident(
        DATABASE_URL,
        req.title,
        req.severity,
        req.started_at,
        req.affected_services,
        tenant_id=auth.tenant_id,
    )
    target = get_tenant_sla_target(auth.tenant_id)
    record_sla_event(
        auth.tenant_id, str(incident_id), "detected", target_minutes=target
    )
    auto_rca = trigger_rca_on_ingest(DATABASE_URL, incident_id)
    return {"incident_id": incident_id, "auto_rca": auto_rca}
