from app.config.scoring_weights import (
    ML_RELIABILITY_MEDIUM,
    ML_RELIABILITY_SMALL,
    ML_SAMPLE_MEDIUM,
    ML_SAMPLE_SMALL,
    RULE_RELIABILITY_NONE,
    RULE_RELIABILITY_ONE,
    RULE_WEIGHT,
    ML_WEIGHT,
)


def compute_ml_reliability(sample_count: int) -> float:
    if sample_count < ML_SAMPLE_SMALL:
        return ML_RELIABILITY_SMALL
    if sample_count < ML_SAMPLE_MEDIUM:
        return ML_RELIABILITY_MEDIUM
    return 1.0


def compute_rule_reliability(evidence_count: int) -> float:
    if evidence_count == 0:
        return RULE_RELIABILITY_NONE
    if evidence_count == 1:
        return RULE_RELIABILITY_ONE
    return 1.0


def compute_hybrid_score(
    rule_confidence: float,
    ml_probability: float,
    *,
    ml_sample_count: int = 0,
    evidence_count: int = 0,
    base_rule_weight: float = None,
    base_ml_weight: float = None,
) -> float:
    if base_rule_weight is None:
        base_rule_weight = RULE_WEIGHT
    if base_ml_weight is None:
        base_ml_weight = ML_WEIGHT

    ml_rel = compute_ml_reliability(ml_sample_count)
    rule_rel = compute_rule_reliability(evidence_count)

    effective_rule_weight = base_rule_weight * rule_rel
    effective_ml_weight = base_ml_weight * ml_rel

    weight_sum = effective_rule_weight + effective_ml_weight
    if weight_sum == 0:
        return 0.0

    effective_rule_weight /= weight_sum
    effective_ml_weight /= weight_sum

    hybrid = (
        effective_rule_weight * rule_confidence
        + effective_ml_weight * ml_probability
    )

    return round(float(hybrid), 6)
