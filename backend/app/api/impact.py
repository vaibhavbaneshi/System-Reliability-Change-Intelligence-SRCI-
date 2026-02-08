import os
from fastapi import APIRouter
from app.ingestion.impact_propagator import propagate_change_impact

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL")

@router.post("/changes/{change_id}/propagate")
def propagate(change_id: str):
    propagate_change_impact(DATABASE_URL, change_id)
    return {"status": "impact propagation completed"}