from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.auth.config import AUTH_ENABLED, AuthContext, DEFAULT_TENANT_ID, PUBLIC_PATHS
from app.auth.keys import validate_api_key
from app.auth.rbac import role_allows
from app.db import get_bypass_connection
from app.tenant.context import set_auth_context


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if not AUTH_ENABLED or path in PUBLIC_PATHS or path.startswith("/metrics"):
            ctx = AuthContext(
                tenant_id=DEFAULT_TENANT_ID,
                role="admin",
                email="system@srci.local",
            )
            set_auth_context(ctx)
            request.state.auth = ctx
            response = await call_next(request)
            return response

        raw_key = self._extract_key(request)
        if not raw_key:
            return JSONResponse(status_code=401, content={"detail": "Missing API key"})

        conn = get_bypass_connection()
        try:
            record = validate_api_key(conn, raw_key)
        finally:
            conn.close()

        if record is None:
            return JSONResponse(status_code=401, content={"detail": "Invalid API key"})

        if not role_allows(record["role"], request.method, path):
            return JSONResponse(
                status_code=403,
                content={"detail": f"Role '{record['role']}' cannot {request.method} {path}"},
            )

        ctx = AuthContext(
            tenant_id=record["tenant_id"],
            role=record["role"],
            user_id=record["user_id"],
            api_key_id=record["id"],
            email=record["email"],
        )
        set_auth_context(ctx)
        request.state.auth = ctx
        return await call_next(request)

    @staticmethod
    def _extract_key(request: Request) -> str | None:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.lower().startswith("bearer "):
            return auth_header[7:].strip()
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return api_key.strip()
        return None
