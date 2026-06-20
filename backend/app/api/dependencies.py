from fastapi import APIRouter
from app.db import get_connection

router = APIRouter()


@router.get("/dependencies")
def list_dependencies():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            d.id,
            d.source_id,
            d.target_id,
            s1.name AS source_service,
            s2.name AS target_service,
            d.dependency_type,
            d.created_at
        FROM dependencies d
        JOIN services s1 ON d.source_id = s1.id
        JOIN services s2 ON d.target_id = s2.id
        ORDER BY s1.name
        """
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": str(r[0]),
            "source_id": str(r[1]),
            "target_id": str(r[2]),
            "source": r[3],
            "target": r[4],
            "dependency_type": r[5],
            "created_at": r[6].isoformat() if r[6] else None,
        }
        for r in rows
    ]
