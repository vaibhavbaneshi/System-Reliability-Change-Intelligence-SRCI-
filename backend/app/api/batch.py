import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.autonomy.batch_runner import run_rca_batch

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL", "")


class BatchRcaRequest(BaseModel):
    limit: int = Field(default=10, ge=1, le=100)
    dry_run: bool = False


@router.post("/rca/batch")
def batch_run_rca(body: BatchRcaRequest):
    return run_rca_batch(DATABASE_URL, limit=body.limit, dry_run=body.dry_run)
