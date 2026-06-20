from app.config.scoring_weights import (
    CLOSE_COMPETITION_DELTA,
    WEAK_SIGNAL_THRESHOLD,
)


def clamp_probability(p: float) -> float:
    if p is None:
        return 0.0
    return max(0.0, min(1.0, float(p)))


def validate_predictions(predictions: list) -> list:
    if not predictions:
        return []

    cleaned = []
    for p in predictions:
        p["ml_probability"] = clamp_probability(p.get("ml_probability", 0.0))
        p["rule_confidence"] = clamp_probability(p.get("rule_confidence", 0.0))
        p["hybrid_score"] = clamp_probability(p.get("hybrid_score", 0.0))
        cleaned.append(p)

    return cleaned


def detect_weak_signal(predictions: list) -> bool:
    if not predictions:
        return True
    return predictions[0]["hybrid_score"] < WEAK_SIGNAL_THRESHOLD


def detect_close_competition(predictions: list) -> bool:
    if len(predictions) < 2:
        return False
    delta = predictions[0]["hybrid_score"] - predictions[1]["hybrid_score"]
    return delta < CLOSE_COMPETITION_DELTA
