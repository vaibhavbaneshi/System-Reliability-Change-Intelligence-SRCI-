import os
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List

from app.auth.config import AuthContext
from app.auth.deps import require_role
from app.ingestion.change_ingestor import ingest_change
from app.graph.blast_radius import compute_blast_radius

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL")


class ChangeRequest(BaseModel):
    change_type: str
    description: str
    git_ref: str
    services_touched: List[str]


@router.post("/changes/ingest")
def ingest_change_api(
    req: ChangeRequest,
    auth: AuthContext = Depends(require_role("admin", "analyst")),
):
    change_id = ingest_change(
        DATABASE_URL,
        req.change_type,
        req.description,
        req.git_ref,
        req.services_touched,
        tenant_id=auth.tenant_id,
    )
    try:
        blast = compute_blast_radius(str(change_id), persist=True)
    except Exception:
        blast = None

    return {
        "change_id": change_id,
        "blast_radius": blast["blast_radius"] if blast else None,
        "upstream_count": len(blast["upstream"]) if blast else 0,
        "downstream_count": len(blast["downstream"]) if blast else 0,
        "risk_panel": blast["risk_panel"] if blast else None,
    }
