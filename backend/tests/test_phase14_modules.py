from app.reasoning.rca_quality import compute_rca_quality
from app.reasoning.failure_analysis import _classify_error, _recommendations


def test_quality_score_with_strong_candidate():
    predictions = [
        {
            "hybrid_score": 0.85,
            "decision_trace": {"components": {"evidence_count": 2}},
        }
    ]
    context_flags = {"weak_signal": False, "close_competition": False}
    escalation = {"should_escalate": False}
    rca_summary = {"confidence_band": "high"}

    result = compute_rca_quality(
        predictions, context_flags, escalation, rca_summary
    )
    assert result["quality_band"] == "high"
    assert result["quality_score"] >= 0.75


def test_quality_score_no_predictions():
    result = compute_rca_quality([], {}, {})
    assert result["quality_score"] == 0.0
    assert result["quality_band"] == "low"


def test_classify_circuit_open():
    assert _classify_error("RCA circuit breaker is open") == "circuit_open"


def test_classify_lock_conflict():
    assert _classify_error("RCA already in progress") == "lock_conflict"


def test_recommendations_high_attempts():
    recs = _recommendations("step_failure", 5)
    assert any("attempt" in r.lower() for r in recs)
