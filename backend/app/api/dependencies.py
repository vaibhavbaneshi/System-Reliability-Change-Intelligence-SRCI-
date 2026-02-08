from fastapi import APIRouter
from app.db import get_connection

router = APIRouter()

@router.get("/dependencies")
def list_dependencies():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            d.id,
            s1.name AS source_service,
            s2.name AS target_service,
            d.created_at
        FROM dependencies d
        JOIN services s1 ON d.source_id = s1.id
        JOIN services s2 ON d.target_id = s2.id
        ORDER BY s1.name
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "source": r[1],
            "target": r[2],
            "created_at": r[3],
        }
        for r in rows
    ]