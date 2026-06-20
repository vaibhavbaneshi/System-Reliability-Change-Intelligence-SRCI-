from fastapi import APIRouter, Depends, HTTPException

from app.auth.config import AuthContext
from app.auth.deps import require_auth
from app.db import get_connection
from app.graph.blast_radius import get_cached_blast_radius

router = APIRouter()


@router.get("/changes/{change_id}/impact")
def get_change_impact(change_id: str, auth: AuthContext = Depends(require_auth)):
    conn = get_connection(tenant_id=auth.tenant_id)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT s.name, ci.impact_level, s.criticality
        FROM change_impacts ci
        JOIN services s ON ci.entity_id = s.id
        WHERE ci.change_id = %s
        ORDER BY
          CASE ci.impact_level
            WHEN 'high' THEN 1
            WHEN 'medium' THEN 2
            WHEN 'low' THEN 3
          END
        """,
        (change_id,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    cached = get_cached_blast_radius(change_id)

    return {
        "change_id": change_id,
        "impacts": [
            {"service": r[0], "impact_level": r[1], "criticality": r[2]}
            for r in rows
        ],
        "blast_radius_summary": cached["blast_radius"] if cached else None,
        "risk_panel": cached["risk_panel"] if cached else None,
    }
