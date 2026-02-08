import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.ingestion.change_ingestor import ingest_change

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL")

class ChangeRequest(BaseModel):
    change_type: str
    description: str
    git_ref: str
    services_touched: List[str]

@router.post("/changes/ingest")
def ingest_change_api(req: ChangeRequest):
    change_id = ingest_change(
        DATABASE_URL,
        req.change_type,
        req.description,
        req.git_ref,
        req.services_touched,
    )
    return {"change_id": change_id}