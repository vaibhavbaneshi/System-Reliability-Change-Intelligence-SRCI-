import os
from fastapi import APIRouter

from app.reasoning.explanation_builder import build_explanation_response

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL", "")


@router.get("/incidents/{incident_id}/explanation")
def explain_incident(incident_id: str):
    return build_explanation_response(DATABASE_URL, incident_id)
