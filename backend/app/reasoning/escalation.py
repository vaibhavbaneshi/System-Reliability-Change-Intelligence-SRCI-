from typing import Optional


def evaluate_escalation(context_flags: dict, rca_summary: Optional[dict]) -> dict:
    """
    Determine whether an RCA result should be escalated for human review.
    """
    weak_signal = bool(context_flags.get("weak_signal"))
    close_competition = bool(context_flags.get("close_competition"))

    hybrid_score = 0.0
    confidence_band = "unknown"
    if rca_summary:
        hybrid_score = float(rca_summary.get("hybrid_score") or 0.0)
        confidence_band = rca_summary.get("confidence_band") or "unknown"

    reasons = []
    if weak_signal:
        reasons.append("weak_signal: top hybrid score below strong-evidence threshold")
    if close_competition:
        reasons.append("close_competition: multiple candidates with similar scores")
    if confidence_band == "low":
        reasons.append("confidence_band: low")
    if hybrid_score < 0.55:
        reasons.append(f"hybrid_score: {hybrid_score:.3f} below escalation threshold")

    should_escalate = bool(reasons)

    if should_escalate:
        level = "review_required"
    elif confidence_band == "medium":
        level = "monitor"
    else:
        level = "none"

    return {
        "should_escalate": should_escalate,
        "escalation_level": level,
        "reasons": reasons,
    }
