def compute_confidence_band(score: float) -> str:
    """
    Convert numeric hybrid score into human band.

    These thresholds are intentionally conservative
    to avoid overconfidence in early-stage models.
    """

    if score >= 0.75:
        return "high"
    elif score >= 0.5:
        return "medium"
    else:
        return "low"