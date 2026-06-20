from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.auth.config import AuthContext
from app.auth.deps import require_auth, require_role
from app.graph.blast_radius import (
    compute_blast_radius,
    compute_service_failure_risk,
    get_cached_blast_radius,
)

router = APIRouter(tags=["graph"])


@router.get("/changes/{change_id}/blast-radius")
def get_blast_radius(change_id: str, auth: AuthContext = Depends(require_auth)):
    cached = get_cached_blast_radius(change_id)
    if cached:
        return cached
    try:
        return compute_blast_radius(change_id, persist=True)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/changes/{change_id}/blast-radius/compute")
def recompute_blast_radius(
    change_id: str,
    auth: AuthContext = Depends(require_role("admin", "analyst")),
):
    try:
        return compute_blast_radius(change_id, persist=True)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/services/{service_id}/failure-risk")
def get_service_failure_risk(
    service_id: str,
    auth: AuthContext = Depends(require_auth),
):
    try:
        return compute_service_failure_risk(service_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
