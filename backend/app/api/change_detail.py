from fastapi import APIRouter
from app.db import get_connection

router = APIRouter()

@router.get("/changes/{change_id}")
def get_change(change_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, change_type, description, git_ref, created_at
        FROM changes
        WHERE id = %s
    """, (change_id,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return {"error": "change not found"}

    return {
        "id": row[0],
        "change_type": row[1],
        "description": row[2],
        "git_ref": row[3],
        "created_at": row[4],
    }