from __future__ import annotations

import os
from datetime import datetime, timezone

from app.db import get_bypass_connection, get_connection
from app.tenant.context import get_current_tenant_id

# Rough Groq pricing estimate per 1M tokens (USD)
COST_PER_MILLION_TOKENS = float(os.getenv("SRCI_LLM_COST_PER_M_TOKENS", "0.59"))


class LLMBudgetExceeded(Exception):
    pass


def _month_start() -> datetime:
    now = datetime.now(timezone.utc)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def get_tenant_budget(tenant_id: str) -> int:
    conn = get_bypass_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT llm_token_budget_monthly FROM tenants WHERE id = %s",
        (tenant_id,),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else 100000


def get_monthly_usage(tenant_id: str) -> int:
    conn = get_bypass_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT COALESCE(SUM(total_tokens), 0)
        FROM llm_usage
        WHERE tenant_id = %s AND created_at >= %s
        """,
        (tenant_id, _month_start()),
    )
    used = int(cur.fetchone()[0])
    cur.close()
    conn.close()
    return used


def check_budget(tenant_id: str | None = None, estimated_tokens: int = 1024) -> None:
    tid = tenant_id or get_current_tenant_id()
    budget = get_tenant_budget(tid)
    used = get_monthly_usage(tid)
    if used + estimated_tokens > budget:
        raise LLMBudgetExceeded(
            f"LLM token budget exceeded: {used}/{budget} tokens used this month"
        )


def record_usage(
    tenant_id: str,
    endpoint: str,
    prompt_tokens: int,
    completion_tokens: int,
    model: str | None = None,
    incident_id: str | None = None,
) -> dict:
    total = prompt_tokens + completion_tokens
    cost = (total / 1_000_000) * COST_PER_MILLION_TOKENS
    conn = get_bypass_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO llm_usage
            (tenant_id, incident_id, endpoint, model, prompt_tokens, completion_tokens,
             total_tokens, estimated_cost_usd)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, total_tokens, estimated_cost_usd
        """,
        (tenant_id, incident_id, endpoint, model, prompt_tokens, completion_tokens, total, cost),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return {
        "id": str(row[0]),
        "total_tokens": row[1],
        "estimated_cost_usd": float(row[2]),
    }


def get_usage_summary(tenant_id: str) -> dict:
    budget = get_tenant_budget(tenant_id)
    used = get_monthly_usage(tenant_id)
    conn = get_bypass_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT endpoint, SUM(total_tokens) AS tokens, SUM(estimated_cost_usd) AS cost
        FROM llm_usage
        WHERE tenant_id = %s AND created_at >= %s
        GROUP BY endpoint
        ORDER BY tokens DESC
        """,
        (tenant_id, _month_start()),
    )
    by_endpoint = [
        {"endpoint": r[0], "tokens": int(r[1]), "cost_usd": float(r[2])}
        for r in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return {
        "budget_tokens": budget,
        "used_tokens": used,
        "remaining_tokens": max(0, budget - used),
        "utilization_pct": round(100 * used / budget, 2) if budget else 0,
        "by_endpoint": by_endpoint,
    }


def estimate_tokens_from_response(response) -> tuple[int, int]:
    usage = getattr(response, "usage", None)
    if usage is not None:
        return (
            getattr(usage, "prompt_tokens", 0) or 0,
            getattr(usage, "completion_tokens", 0) or 0,
        )
    # Fallback estimate from content length
    try:
        content = response.choices[0].message.content or ""
        return (512, max(1, len(content) // 4))
    except Exception:
        return (512, 512)
