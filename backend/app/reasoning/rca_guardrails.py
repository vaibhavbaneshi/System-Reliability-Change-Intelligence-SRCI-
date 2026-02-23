def clamp_probability(p: float) -> float:
    """Ensure probability stays in valid bounds."""
    if p is None:
        return 0.0
    return max(0.0, min(1.0, float(p)))


def validate_predictions(predictions: list) -> list:
    """
    Sanity-check prediction list.
    Prevents bad ML output from breaking ranking.
    """
    if not predictions:
        return []

    cleaned = []

    for p in predictions:
        p["ml_probability"] = clamp_probability(
            p.get("ml_probability", 0.0)
        )
        p["rule_confidence"] = clamp_probability(
            p.get("rule_confidence", 0.0)
        )
        p["hybrid_score"] = clamp_probability(
            p.get("hybrid_score", 0.0)
        )

        cleaned.append(p)

    return cleaned


def detect_weak_signal(predictions: list) -> bool:
    """
    Detect when RCA signal is weak.
    Used for explanation tone control.
    """
    if not predictions:
        return True

    top = predictions[0]["hybrid_score"]

    # weak if below meaningful threshold
    return top < 0.55


def detect_close_competition(predictions: list) -> bool:
    """
    Detect if top candidates are too close.
    """
    if len(predictions) < 2:
        return False

    delta = predictions[0]["hybrid_score"] - predictions[1]["hybrid_score"]
    return delta < 0.08