from fastapi import APIRouter
import os
from app.reasoning.context_builder import build_incident_context

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL", "")


@router.get("/incidents/{incident_id}/reasoning")
def get_reasoning(incident_id: str):
    context = build_incident_context(DATABASE_URL, incident_id)

    return {
        "incident_id": incident_id,
        "reasoning": context
    }