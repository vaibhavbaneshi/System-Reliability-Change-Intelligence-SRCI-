import os
from fastapi import APIRouter
from app.ingestion.evidence_linker import link_change_evidence

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL", "")

@router.post("/incidents/{incident_id}/evidence")
def generate_evidence(incident_id: str):
    link_change_evidence(DATABASE_URL, incident_id)
    return {
        "incident_id": incident_id,
        "status": "evidence linked"
    }