import os
from fastapi import APIRouter
from app.ml.predictor import predict_for_incident

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL")

@router.post("/incidents/{incident_id}/predict")
def predict(incident_id: str):
    return predict_for_incident(DATABASE_URL, incident_id)