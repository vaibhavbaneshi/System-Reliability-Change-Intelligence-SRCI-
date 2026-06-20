import os
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.ml.label_assigner import assign_labels_for_incident

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL", "")


class LabelEntry(BaseModel):
    change_id: str
    label: int = Field(..., ge=0, le=1)


class LabelAssignmentRequest(BaseModel):
    labels: List[LabelEntry]


@router.post("/incidents/{incident_id}/labels")
def set_incident_labels(incident_id: str, body: LabelAssignmentRequest):
    try:
        return assign_labels_for_incident(
            DATABASE_URL,
            incident_id,
            [entry.model_dump() for entry in body.labels],
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
