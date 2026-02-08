import os
from fastapi import APIRouter
from app.ingestion.incident_change_correlator import correlate_incident_to_changes

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL" ,"")

@router.post("/incidents/{incident_id}/correlate")
def correlate_incident(incident_id: str):
    hypotheses = correlate_incident_to_changes(DATABASE_URL, incident_id)
    return {
        "incident_id": incident_id,
        "hypotheses_found": len(hypotheses),
    }