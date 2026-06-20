from __future__ import annotations

import json
import os

from groq import Groq

from app.genai.prompts import EXPLANATION_PROMPT
from app.enterprise.llm_budget import (
    LLMBudgetExceeded,
    check_budget,
    estimate_tokens_from_response,
    record_usage,
)
from app.tenant.context import get_current_tenant_id

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def _llm_enabled() -> bool:
    return os.getenv("SRCI_USE_LLM_EXPLANATIONS", "true").lower() in (
        "1",
        "true",
        "yes",
    )


def _get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


def _no_candidates_message() -> str:
    return (
        "No strong root-cause candidates were identified for this incident. "
        "Additional telemetry or change data may be required."
    )


def _generate_template_explanation(context: dict) -> str:
    candidates = context.get("candidates", [])
    services = context.get("affected_services", [])

    if not candidates:
        return _no_candidates_message()

    top = candidates[0]
    top_desc = top.get("change_description") or "Unknown change"
    top_score = top.get("hybrid_score", 0.0)
    top_band = top.get("confidence_band", "unknown")

    runner_up_note = ""
    if len(candidates) > 1:
        second = candidates[1]
        gap = top_score - second.get("hybrid_score", 0)
        if gap < 0.15:
            second_desc = second.get("change_description") or "another change"
            runner_up_note = (
                f"\n\n⚠️ **Competing hypothesis detected:** "
                f"{second_desc} has a comparable score. "
                "Confidence should be treated as moderate."
            )

    band_guidance = {
        "high": "strong statistical and rule-based alignment",
        "medium": "reasonable but not definitive evidence",
        "low": "weak correlation — manual validation recommended",
    }
    band_text = band_guidance.get(top_band, "uncertain confidence")

    service_names = [s["name"] for s in services]
    service_text = ", ".join(service_names) if service_names else "the impacted service"

    flags = context.get("context_flags", {})
    uncertainty_note = ""
    if flags.get("weak_signal"):
        uncertainty_note = (
            "\n\n⚠️ **Weak signal:** Confidence is below the strong-evidence threshold. "
            "Treat this as a hypothesis, not a confirmed root cause."
        )

    return f"""
**Executive Summary**

The incident affecting {service_text} most likely correlates with **{top_desc}**.

- Hybrid score: **{top_score:.3f}**
- Confidence band: **{top_band}**
- Interpretation: {band_text}

**Technical Reasoning**

- Temporal proximity and service impact signals align with the incident window.
- Rule-based correlation and ML scoring both elevate this change above other candidates.
- No stronger competing change was identified.

{runner_up_note}{uncertainty_note}

**Recommended Action**

Validate this deployment/change via logs, metrics, and recent configuration diffs before final incident closure.
""".strip()


def _generate_llm_explanation(
    context: dict,
    client: Groq,
    *,
    endpoint: str = "explain",
    incident_id: str | None = None,
) -> str:
    tenant_id = get_current_tenant_id()
    check_budget(tenant_id, estimated_tokens=1024)

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": EXPLANATION_PROMPT},
            {
                "role": "user",
                "content": json.dumps(context, indent=2, default=str),
            },
        ],
        temperature=0.2,
        max_tokens=1024,
    )
    prompt_tokens, completion_tokens = estimate_tokens_from_response(response)
    record_usage(
        tenant_id,
        endpoint,
        prompt_tokens,
        completion_tokens,
        model=GROQ_MODEL,
        incident_id=incident_id,
    )

    content = response.choices[0].message.content
    if not content or not content.strip():
        raise ValueError("Empty LLM response")
    return content.strip()


def generate_explanation(
    context: dict,
    *,
    endpoint: str = "explain",
    incident_id: str | None = None,
) -> dict:
    """
    Returns {"explanation": str, "source": "llm" | "template"}.
    Falls back to template if LLM is disabled, unavailable, budget exceeded, or errors.
    """
    if not context.get("candidates"):
        return {"explanation": _no_candidates_message(), "source": "template"}

    if _llm_enabled():
        client = _get_client()
        if client is not None:
            try:
                text = _generate_llm_explanation(
                    context,
                    client,
                    endpoint=endpoint,
                    incident_id=incident_id,
                )
                return {"explanation": text, "source": "llm"}
            except LLMBudgetExceeded:
                return {
                    "explanation": _generate_template_explanation(context),
                    "source": "template",
                    "budget_exceeded": True,
                }
            except Exception:
                pass

    return {
        "explanation": _generate_template_explanation(context),
        "source": "template",
    }
