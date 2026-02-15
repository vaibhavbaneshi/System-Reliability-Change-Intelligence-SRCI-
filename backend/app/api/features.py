import os
from fastapi import APIRouter
from app.ml.feature_builder import build_features_for_incident

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL")

@router.post("/incidents/{incident_id}/features")
def generate_features(incident_id: str):
    build_features_for_incident(DATABASE_URL, incident_id)
    return {
        "incident_id": incident_id,
        "status": "features generated"
    }