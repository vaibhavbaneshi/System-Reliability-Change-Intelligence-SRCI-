from fastapi import APIRouter
from app.db import get_connection

router = APIRouter()

@router.get("/changes")
def list_changes():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, change_type, description, git_ref, created_at
        FROM changes
        ORDER BY created_at DESC
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "change_type": r[1],
            "description": r[2],
            "git_ref": r[3],
            "created_at": r[4],
        }
        for r in rows
    ]