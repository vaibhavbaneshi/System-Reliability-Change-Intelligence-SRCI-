def compute_ml_reliability(sample_count: int) -> float:
    """
    Estimate ML trust based on training data size.
    """
    if sample_count < 10:
        return 0.4
    if sample_count < 50:
        return 0.7
    return 1.0


def compute_rule_reliability(evidence_count: int) -> float:
    """
    Estimate rule trust based on supporting evidence.
    """
    if evidence_count == 0:
        return 0.6
    if evidence_count == 1:
        return 0.8
    return 1.0


def compute_hybrid_score(
    rule_confidence: float,
    ml_probability: float,
    *,
    ml_sample_count: int = 0,
    evidence_count: int = 0,
    base_rule_weight: float = 0.6,
    base_ml_weight: float = 0.4,
) -> float:
    """
    Production-style hybrid fusion with reliability calibration.
    """

    # 🔹 Reliability factors
    ml_rel = compute_ml_reliability(ml_sample_count)
    rule_rel = compute_rule_reliability(evidence_count)

    # 🔹 Effective weights
    effective_rule_weight = base_rule_weight * rule_rel
    effective_ml_weight = base_ml_weight * ml_rel

    # 🔹 Normalize weights
    weight_sum = effective_rule_weight + effective_ml_weight
    if weight_sum == 0:
        return 0.0

    effective_rule_weight /= weight_sum
    effective_ml_weight /= weight_sum

    # 🔹 Final fusion
    hybrid = (
        effective_rule_weight * rule_confidence
        + effective_ml_weight * ml_probability
    )

    return round(float(hybrid), 6)