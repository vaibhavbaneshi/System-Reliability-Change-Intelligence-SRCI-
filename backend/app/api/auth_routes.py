from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from pydantic import BaseModel

from app.auth.config import AuthContext, OAUTH_ENABLED, OAUTH_ISSUER
from app.auth.deps import generate_api_key, require_admin, require_auth
from app.auth.keys import hash_api_key, key_prefix
from app.db import get_bypass_connection

router = APIRouter(prefix="/auth", tags=["auth"])


class ApiKeyCreateRequest(BaseModel):
    name: str = "default"
    role: str = "analyst"


class OAuthCallbackRequest(BaseModel):
    code: str
    redirect_uri: Optional[str] = None


@router.get("/me")
def get_current_user(auth: AuthContext = Depends(require_auth)):
    return {
        "tenant_id": auth.tenant_id,
        "role": auth.role,
        "user_id": auth.user_id,
        "email": auth.email,
        "auth_enabled": os.getenv("SRCI_AUTH_ENABLED", "false"),
    }


@router.post("/api-keys")
def create_api_key(
    req: ApiKeyCreateRequest,
    auth: AuthContext = Depends(require_admin),
):
    if req.role not in ("admin", "analyst", "viewer"):
        raise HTTPException(status_code=400, detail="Invalid role")

    raw_key = generate_api_key()
    conn = get_bypass_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO api_keys (tenant_id, user_id, name, key_prefix, key_hash, role)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, created_at
        """,
        (
            auth.tenant_id,
            auth.user_id,
            req.name,
            key_prefix(raw_key),
            hash_api_key(raw_key),
            req.role,
        ),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return {
        "id": str(row[0]),
        "api_key": raw_key,
        "name": req.name,
        "role": req.role,
        "created_at": row[1].isoformat(),
        "note": "Store this key securely — it will not be shown again.",
    }


@router.get("/api-keys")
def list_api_keys(auth: AuthContext = Depends(require_admin)):
    conn = get_bypass_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, name, key_prefix, role, created_at, last_used_at, revoked_at
        FROM api_keys
        WHERE tenant_id = %s
        ORDER BY created_at DESC
        """,
        (auth.tenant_id,),
    )
    keys = [
        {
            "id": str(r[0]),
            "name": r[1],
            "key_prefix": r[2],
            "role": r[3],
            "created_at": r[4].isoformat(),
            "last_used_at": r[5].isoformat() if r[5] else None,
            "revoked": r[6] is not None,
        }
        for r in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return {"api_keys": keys}


@router.delete("/api-keys/{key_id}")
def revoke_api_key(key_id: str, auth: AuthContext = Depends(require_admin)):
    conn = get_bypass_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE api_keys SET revoked_at = NOW()
        WHERE id = %s AND tenant_id = %s AND revoked_at IS NULL
        RETURNING id
        """,
        (key_id, auth.tenant_id),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="API key not found")
    return {"revoked": True, "id": key_id}


@router.post("/oauth/callback")
def oauth_callback(req: OAuthCallbackRequest):
    """
    OAuth2 callback stub. Enable with SRCI_OAUTH_ENABLED=true and configure
    SRCI_OAUTH_CLIENT_ID / SRCI_OAUTH_CLIENT_SECRET / SRCI_OAUTH_ISSUER.
    """
    if not OAUTH_ENABLED:
        raise HTTPException(
            status_code=501,
            detail="OAuth is disabled. Set SRCI_OAUTH_ENABLED=true to enable.",
        )

    if not req.code:
        raise HTTPException(status_code=400, detail="Authorization code required")

    return {
        "status": "stub",
        "message": (
            f"OAuth callback received for issuer {OAUTH_ISSUER}. "
            "Wire token exchange to your IdP in production."
        ),
        "code_received": bool(req.code),
    }


@router.get("/login")
def login_info():
    return {
        "methods": ["api_key"],
        "oauth_enabled": OAUTH_ENABLED,
        "headers": {
            "Authorization": "Bearer <api_key>",
            "X-API-Key": "<api_key>",
        },
        "demo_key": "srci_demo_key (when SRCI_AUTH_ENABLED=true)",
    }
