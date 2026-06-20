from __future__ import annotations

import hashlib
from datetime import datetime, timezone


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def key_prefix(raw_key: str) -> str:
    return raw_key[:12] if len(raw_key) >= 12 else raw_key


def validate_api_key(conn, raw_key: str) -> dict | None:
    """Returns key record dict or None if invalid."""
    prefix = key_prefix(raw_key)
    key_hash = hash_api_key(raw_key)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT ak.id, ak.tenant_id, ak.user_id, ak.role, ak.expires_at, ak.revoked_at,
               u.email
        FROM api_keys ak
        LEFT JOIN users u ON u.id = ak.user_id
        WHERE ak.key_hash = %s
        LIMIT 1
        """,
        (key_hash,),
    )
    row = cur.fetchone()
    if row is None:
        cur.close()
        return None

    record = {
        "id": str(row[0]),
        "tenant_id": str(row[1]),
        "user_id": str(row[2]) if row[2] else None,
        "role": row[3],
        "expires_at": row[4],
        "revoked_at": row[5],
        "email": row[6],
    }

    if record["revoked_at"] is not None:
        cur.close()
        return None

    if record["expires_at"] is not None:
        expires = record["expires_at"]
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires < datetime.now(timezone.utc):
            cur.close()
            return None

    cur.execute(
        "UPDATE api_keys SET last_used_at = NOW() WHERE id = %s",
        (record["id"],),
    )
    conn.commit()
    cur.close()
    return record
