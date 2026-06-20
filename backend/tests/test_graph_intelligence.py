from __future__ import annotations

from app.config.settings import dependency_weight, DEPTH_DECAY
from app.graph.blast_radius import (
    _impact_level,
    _risk_band,
    compute_failure_spread,
    compute_risk_panel,
)


def test_dependency_weight_known_type():
    assert dependency_weight("http") == 0.75
    assert dependency_weight("runtime") == 1.0


def test_dependency_weight_unknown():
    assert dependency_weight("unknown_type") == 0.5


def test_impact_level_thresholds():
    assert _impact_level(0.8) == "high"
    assert _impact_level(0.5) == "medium"
    assert _impact_level(0.2) == "low"


def test_risk_band_thresholds():
    assert _risk_band(0.75) == "high"
    assert _risk_band(0.5) == "medium"
    assert _risk_band(0.2) == "low"


def test_failure_spread_empty():
    result = compute_failure_spread([], [], [])
    assert result["expected_affected_count"] == 0.0
    assert result["high_risk_count"] == 0


def test_failure_spread_with_nodes():
    nodes = [
        {"impact_level": "high", "propagation_probability": 0.9},
        {"impact_level": "medium", "propagation_probability": 0.5},
    ]
    result = compute_failure_spread([], nodes, [])
    assert result["high_risk_count"] == 1
    assert result["medium_risk_count"] == 1
    assert result["expected_affected_count"] == 1.4


def test_risk_panel_with_origins():
    origins = [
        {
            "criticality": "high",
            "risk_contribution": 1.0,
            "propagation_probability": 1.0,
            "impact_level": "high",
        }
    ]
    panel = compute_risk_panel([], [], origins)
    assert panel["risk_band"] in ("high", "medium", "low")
    assert panel["overall_risk_score"] > 0
    assert len(panel["factors"]) >= 1


def test_depth_decay_constant():
    assert 0 < DEPTH_DECAY < 1
