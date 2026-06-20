import os

from app.genai.explainer import generate_explanation
from app.reasoning.escalation import evaluate_escalation


def test_template_explanation_when_llm_disabled(monkeypatch):
    monkeypatch.setenv("SRCI_USE_LLM_EXPLANATIONS", "false")
    context = {
        "candidates": [
            {
                "change_id": "abc",
                "change_description": "auth token validation change",
                "hybrid_score": 0.526,
                "confidence_band": "medium",
            }
        ],
        "affected_services": [{"id": "1", "name": "auth-service"}],
        "context_flags": {"weak_signal": True, "close_competition": False},
    }
    result = generate_explanation(context)
    assert result["source"] == "template"
    assert "auth token validation" in result["explanation"]
    assert "Weak signal" in result["explanation"]


def test_escalation_on_weak_signal():
    result = evaluate_escalation(
        {"weak_signal": True, "close_competition": False},
        {"hybrid_score": 0.526, "confidence_band": "medium"},
    )
    assert result["should_escalate"] is True
    assert result["escalation_level"] == "review_required"
    assert any("weak_signal" in r for r in result["reasons"])


def test_no_escalation_on_strong_signal():
    result = evaluate_escalation(
        {"weak_signal": False, "close_competition": False},
        {"hybrid_score": 0.85, "confidence_band": "high"},
    )
    assert result["should_escalate"] is False
    assert result["escalation_level"] == "none"
