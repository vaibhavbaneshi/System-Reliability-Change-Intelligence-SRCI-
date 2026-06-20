from typing import Optional


def compute_rca_quality(
    predictions: list,
    context_flags: dict,
    escalation: dict,
    rca_summary: Optional[dict] = None,
) -> dict:
    """
    Composite RCA quality score from existing pipeline signals.
    """
    factors = []
    score = 0.0

    if not predictions:
        return {
            "quality_score": 0.0,
            "quality_band": "low",
            "factors": ["no_predictions"],
        }

    top = predictions[0]
    hybrid = float(top.get("hybrid_score", 0.0))
    components = top.get("decision_trace", {}).get("components", {})
    evidence_count = int(components.get("evidence_count", 0))

    score += hybrid * 0.45
    factors.append(f"hybrid_score: {hybrid:.3f}")

    if not context_flags.get("weak_signal"):
        score += 0.15
        factors.append("strong_signal")
    else:
        factors.append("weak_signal_penalty")

    if not context_flags.get("close_competition"):
        score += 0.1
        factors.append("clear_winner")
    else:
        factors.append("close_competition_penalty")

    if evidence_count >= 1:
        score += 0.1
        factors.append(f"evidence_count: {evidence_count}")
    else:
        factors.append("no_evidence")

    if len(predictions) >= 2:
        score += 0.05
        factors.append("multiple_candidates_scored")

    if escalation and not escalation.get("should_escalate"):
        score += 0.15
        factors.append("no_escalation_required")
    elif escalation and escalation.get("should_escalate"):
        factors.append("escalation_required")

    if rca_summary and rca_summary.get("confidence_band") == "high":
        score += 0.05
        factors.append("high_confidence_band")

    score = round(min(1.0, max(0.0, score)), 4)

    if score >= 0.75:
        band = "high"
    elif score >= 0.5:
        band = "medium"
    else:
        band = "low"

    return {
        "quality_score": score,
        "quality_band": band,
        "factors": factors,
    }
