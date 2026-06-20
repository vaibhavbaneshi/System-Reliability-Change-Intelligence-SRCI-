import os

from fastapi import APIRouter, Depends, HTTPException

from app.auth.config import AuthContext
from app.auth.deps import require_admin, require_auth, require_role
from app.enterprise.canary import get_canary_history, run_canary_scoring
from app.enterprise.chaos import get_chaos_history, run_chaos_scenario
from app.enterprise.drift import compute_drift, get_drift_history
from app.enterprise.llm_budget import get_usage_summary

router = APIRouter(prefix="/enterprise", tags=["enterprise"])
DATABASE_URL = os.getenv("DATABASE_URL", "")


@router.get("/llm-usage")
def llm_usage(auth: AuthContext = Depends(require_auth)):
    return get_usage_summary(auth.tenant_id)


@router.post("/drift/compute")
def drift_compute(
    window_hours: int = 24,
    auth: AuthContext = Depends(require_role("admin", "analyst")),
):
    return compute_drift(auth.tenant_id, window_hours=window_hours)


@router.get("/drift/history")
def drift_history(limit: int = 50, auth: AuthContext = Depends(require_auth)):
    return {"snapshots": get_drift_history(auth.tenant_id, limit=limit)}


@router.post("/canary/{incident_id}")
def canary_score(
    incident_id: str,
    auth: AuthContext = Depends(require_role("admin", "analyst")),
):
    return run_canary_scoring(auth.tenant_id, incident_id)


@router.get("/canary/history")
def canary_history(limit: int = 50, auth: AuthContext = Depends(require_auth)):
    return {"predictions": get_canary_history(auth.tenant_id, limit=limit)}


@router.post("/chaos/run")
def chaos_run(
    scenario: str = "deployment_correlation",
    auth: AuthContext = Depends(require_admin),
):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL not configured")
    return run_chaos_scenario(DATABASE_URL, auth.tenant_id, scenario=scenario)


@router.get("/chaos/history")
def chaos_history(limit: int = 20, auth: AuthContext = Depends(require_auth)):
    return {"runs": get_chaos_history(auth.tenant_id, limit=limit)}


@router.get("/tenants/me")
def tenant_info(auth: AuthContext = Depends(require_auth)):
    from app.db import get_bypass_connection

    conn = get_bypass_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, name, slug, plan, llm_token_budget_monthly, sla_target_minutes, created_at
        FROM tenants WHERE id = %s
        """,
        (auth.tenant_id,),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {
        "id": str(row[0]),
        "name": row[1],
        "slug": row[2],
        "plan": row[3],
        "llm_token_budget_monthly": row[4],
        "sla_target_minutes": row[5],
        "created_at": row[6].isoformat(),
    }
