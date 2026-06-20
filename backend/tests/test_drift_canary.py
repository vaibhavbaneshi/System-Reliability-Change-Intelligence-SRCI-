from app.reasoning.hybrid_scorer import compute_hybrid_score
from app.config.scoring_weights import ML_WEIGHT, RULE_WEIGHT


def test_canary_weights_produce_valid_score():
    rule, ml = 0.8, 0.6
    canary = compute_hybrid_score(
        rule, ml, base_rule_weight=RULE_WEIGHT - 0.05, base_ml_weight=ML_WEIGHT + 0.05
    )
    assert 0.0 <= canary <= 1.0


def test_drift_threshold_constant():
    from app.enterprise.drift import DRIFT_THRESHOLD

    assert DRIFT_THRESHOLD == 2.0
