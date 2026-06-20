from __future__ import annotations

import os
from dataclasses import dataclass

AUTH_ENABLED = os.getenv("SRCI_AUTH_ENABLED", "false").lower() in ("1", "true", "yes")
DEFAULT_TENANT_ID = os.getenv(
    "SRCI_DEFAULT_TENANT_ID", "00000000-0000-4000-a000-000000000001"
)
OAUTH_ENABLED = os.getenv("SRCI_OAUTH_ENABLED", "false").lower() in ("1", "true", "yes")
OAUTH_CLIENT_ID = os.getenv("SRCI_OAUTH_CLIENT_ID", "")
OAUTH_CLIENT_SECRET = os.getenv("SRCI_OAUTH_CLIENT_SECRET", "")
OAUTH_ISSUER = os.getenv("SRCI_OAUTH_ISSUER", "https://accounts.google.com")

PUBLIC_PATHS = frozenset(
    {
        "/",
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/auth/login",
        "/auth/oauth/callback",
        "/webhooks/github",
    }
)


@dataclass(frozen=True)
class AuthContext:
    tenant_id: str
    role: str
    user_id: str | None = None
    api_key_id: str | None = None
    email: str | None = None

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"
