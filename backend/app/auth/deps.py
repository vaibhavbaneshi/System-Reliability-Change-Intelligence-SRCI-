import secrets
import uuid

from fastapi import Depends, HTTPException, Request

from app.auth.config import AUTH_ENABLED, AuthContext, DEFAULT_TENANT_ID
from app.auth.rbac import role_allows
from app.tenant.context import get_auth_context, set_auth_context


def _default_context() -> AuthContext:
    return AuthContext(
        tenant_id=DEFAULT_TENANT_ID,
        role="admin",
        email="system@srci.local",
    )


def get_request_auth(request: Request) -> AuthContext:
    ctx = get_auth_context()
    if ctx is not None:
        return ctx
    if hasattr(request.state, "auth") and request.state.auth:
        return request.state.auth
    return _default_context()


def require_auth(request: Request) -> AuthContext:
    ctx = get_request_auth(request)
    if AUTH_ENABLED and not hasattr(request.state, "auth"):
        raise HTTPException(status_code=401, detail="Authentication required")
    return ctx


def require_role(*allowed_roles: str):
    def checker(request: Request, auth: AuthContext = Depends(require_auth)) -> AuthContext:
        if auth.role not in allowed_roles and auth.role != "admin":
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        if not role_allows(auth.role, request.method, request.url.path):
            raise HTTPException(status_code=403, detail="Operation not permitted for role")
        return auth

    return checker


def require_admin(auth: AuthContext = Depends(require_auth)) -> AuthContext:
    if auth.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return auth


def generate_api_key() -> str:
    return f"srci_{secrets.token_urlsafe(32)}"
