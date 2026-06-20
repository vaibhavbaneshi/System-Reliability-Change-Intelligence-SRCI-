from __future__ import annotations

from contextvars import ContextVar

from app.auth.config import AuthContext, DEFAULT_TENANT_ID

_auth_context: ContextVar[AuthContext | None] = ContextVar("auth_context", default=None)


def set_auth_context(ctx: AuthContext) -> None:
    _auth_context.set(ctx)


def get_auth_context() -> AuthContext | None:
    return _auth_context.get()


def get_current_tenant_id() -> str:
    ctx = get_auth_context()
    if ctx is not None:
        return ctx.tenant_id
    return DEFAULT_TENANT_ID


def get_current_role() -> str:
    ctx = get_auth_context()
    if ctx is not None:
        return ctx.role
    return "admin"
