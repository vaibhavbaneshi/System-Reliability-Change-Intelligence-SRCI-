from app.reasoning.rca_guardrails import (
    clamp_probability,
    detect_close_competition,
    detect_weak_signal,
    validate_predictions,
)
from app.config.scoring_weights import WEAK_SIGNAL_THRESHOLD, CLOSE_COMPETITION_DELTA
from app.reasoning.hybrid_scorer import compute_hybrid_score, compute_ml_reliability


def test_clamp_probability_bounds():
    assert clamp_probability(1.5) == 1.0
    assert clamp_probability(-0.5) == 0.0
    assert clamp_probability(None) == 0.0


def test_validate_predictions_clamps():
    preds = [{"ml_probability": 2.0, "rule_confidence": -1, "hybrid_score": 0.5}]
    cleaned = validate_predictions(preds)
    assert cleaned[0]["ml_probability"] == 1.0
    assert cleaned[0]["rule_confidence"] == 0.0


def test_weak_signal_detection():
    assert detect_weak_signal([{"hybrid_score": 0.1}]) is True
    assert detect_weak_signal([{"hybrid_score": 0.9}]) is False
    assert detect_weak_signal([]) is True


def test_close_competition():
    preds = [{"hybrid_score": 0.6}, {"hybrid_score": 0.55}]
    assert detect_close_competition(preds) is True
    preds = [{"hybrid_score": 0.9}, {"hybrid_score": 0.3}]
    assert detect_close_competition(preds) is False


def test_hybrid_score_weighted():
    score = compute_hybrid_score(0.8, 0.6, ml_sample_count=100, evidence_count=2)
    assert 0.0 <= score <= 1.0


def test_ml_reliability_small_sample():
    assert compute_ml_reliability(5) < compute_ml_reliability(100)
