from fastapi import APIRouter
from app.db import get_connection

router = APIRouter()

@router.get("/services")
def list_services():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, owner_team, criticality, created_at
        FROM services
        ORDER BY name
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "name": r[1],
            "owner_team": r[2],
            "criticality": r[3],
            "created_at": r[4],
        }
        for r in rows
    ]