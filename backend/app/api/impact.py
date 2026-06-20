import os
from fastapi import APIRouter, Depends

from app.auth.config import AuthContext
from app.auth.deps import require_role
from app.graph.impact_propagation import propagate_change_impact_weighted

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL")


@router.post("/changes/{change_id}/propagate")
def propagate(
    change_id: str,
    auth: AuthContext = Depends(require_role("admin", "analyst")),
):
    return propagate_change_impact_weighted(DATABASE_URL, change_id)
