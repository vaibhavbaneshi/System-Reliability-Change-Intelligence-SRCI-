import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.ingestion.incident_ingestor import ingest_incident
from app.autonomy.event_handler import trigger_rca_on_ingest

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL")

class IncidentRequest(BaseModel):
    title: str
    severity: str
    started_at: datetime
    affected_services: List[str]

@router.post("/incidents/ingest")
def ingest_incident_api(req: IncidentRequest):
    incident_id = ingest_incident(
        DATABASE_URL,
        req.title,
        req.severity,
        req.started_at,
        req.affected_services,
    )
    auto_rca = trigger_rca_on_ingest(DATABASE_URL, incident_id)
    return {"incident_id": incident_id, "auto_rca": auto_rca}