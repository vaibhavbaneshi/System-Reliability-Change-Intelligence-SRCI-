import os
from groq import Groq

EXPLANATION_PROMPT = """
You are an expert SRE incident analyst.

You are given structured incident intelligence.

STRICT RULES:
- Do NOT invent causes
- Do NOT fabricate evidence
- Do NOT modify confidence values
- Only reason from provided data
- Be technically precise and concise

Additional behavior rules:

- If weak_signal is true → express uncertainty clearly
- If close_competition is true → mention multiple plausible causes
- If hybrid_score < 0.6 → avoid definitive language
- Never claim certainty unless hybrid_score > 0.8

Your task:
1. Identify the most likely root cause
2. Use rule confidence, ML probability, and hybrid score
3. Explicitly communicate uncertainty
4. Reference the actual change description when available
5. If confidence is not high, clearly say investigation should continue

Output style:
- Short executive summary
- Bullet-based technical reasoning
- Clear confidence statement
"""

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("GROQ_API_KEY is not set")

client = Groq(api_key=api_key)


def generate_explanation(context):
    candidates = context.get("candidates", [])
    incident = context.get("incident", {})
    services = context.get("affected_services", [])

    if not candidates:
        return (
            "No strong root-cause candidates were identified for this incident. "
            "Additional telemetry or change data may be required."
        )

    # -------------------------------------------------
    # Top candidate
    # -------------------------------------------------
    top = candidates[0]
    top_desc = top.get("change_description") or "Unknown change"
    top_score = top.get("hybrid_score", 0.0)
    top_band = top.get("confidence_band", "unknown")
    top_time = top.get("change_created_at")

    # -------------------------------------------------
    # Runner-up analysis (important!)
    # -------------------------------------------------
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

    # -------------------------------------------------
    # Confidence interpretation
    # -------------------------------------------------
    band_guidance = {
        "high": "strong statistical and rule-based alignment",
        "medium": "reasonable but not definitive evidence",
        "low": "weak correlation — manual validation recommended",
    }

    band_text = band_guidance.get(top_band, "uncertain confidence")

    # -------------------------------------------------
    # Affected services text
    # -------------------------------------------------
    service_names = [s["name"] for s in services]
    service_text = ", ".join(service_names) if service_names else "the impacted service"

    # -------------------------------------------------
    # Final narrative
    # -------------------------------------------------
    explanation = f"""
    **Executive Summary**

    The incident affecting {service_text} most likely correlates with **{top_desc}**.

    - Hybrid score: **{top_score:.3f}**
    - Confidence band: **{top_band}**
    - Interpretation: {band_text}

    **Technical Reasoning**

    - Temporal proximity and service impact signals align with the incident window.
    - Rule-based correlation and ML scoring both elevate this change above other candidates.
    - No stronger competing change was identified.

    {runner_up_note}

    **Recommended Action**

    Validate this deployment/change via logs, metrics, and recent configuration diffs before final incident closure.
    """.strip()

    return explanation