from fastapi import APIRouter
from app.db import get_connection

router = APIRouter()

@router.get("/changes")
def list_changes():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, change_type, description, git_ref, created_at,
               COALESCE(source, 'manual') AS source, commit_sha, pr_number
        FROM changes
        ORDER BY created_at DESC
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": str(r[0]),
            "change_type": r[1],
            "description": r[2],
            "git_ref": r[3],
            "created_at": r[4].isoformat() if r[4] else None,
            "source": r[5],
            "commit_sha": r[6],
            "pr_number": r[7],
        }
        for r in rows
    ]