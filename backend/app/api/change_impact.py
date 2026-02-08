from fastapi import APIRouter
from app.db import get_connection

router = APIRouter()

@router.get("/changes/{change_id}/impact")
def get_change_impact(change_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            s.name,
            ci.impact_level
        FROM change_impacts ci
        JOIN services s ON ci.entity_id = s.id
        WHERE ci.change_id = %s
        ORDER BY
          CASE ci.impact_level
            WHEN 'high' THEN 1
            WHEN 'medium' THEN 2
            WHEN 'low' THEN 3
          END
    """, (change_id,))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "service": r[0],
            "impact_level": r[1],
        }
        for r in rows
    ]