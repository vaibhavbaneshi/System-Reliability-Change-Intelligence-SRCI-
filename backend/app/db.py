from __future__ import annotations

import os

import psycopg2
from psycopg2.extras import RealDictCursor

from app.auth.config import DEFAULT_TENANT_ID
from app.tenant.context import get_current_tenant_id

DATABASE_URL = os.getenv("DATABASE_URL")


def _apply_session_settings(cur, tenant_id: str | None, bypass_rls: bool) -> None:
    if bypass_rls:
        cur.execute("SET app.bypass_rls = 'true'")
    else:
        cur.execute("RESET app.bypass_rls")
        tid = tenant_id or get_current_tenant_id() or DEFAULT_TENANT_ID
        cur.execute("SET app.tenant_id = %s", (tid,))


def get_connection(tenant_id: str | None = None, bypass_rls: bool = False):
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cur:
        _apply_session_settings(cur, tenant_id, bypass_rls)
    return conn


def get_bypass_connection():
    """Internal operations (auth lookup, autonomy monitor) bypass RLS."""
    return get_connection(bypass_rls=True)


def get_dict_cursor_connection(tenant_id: str | None = None, bypass_rls: bool = False):
    conn = get_connection(tenant_id=tenant_id, bypass_rls=bypass_rls)
    conn.cursor_factory = RealDictCursor
    return conn
