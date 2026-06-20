from app.config.scoring_weights import CONFIDENCE_BAND_HIGH, CONFIDENCE_BAND_MEDIUM


def compute_confidence_band(score: float) -> str:
    if score >= CONFIDENCE_BAND_HIGH:
        return "high"
    if score >= CONFIDENCE_BAND_MEDIUM:
        return "medium"
    return "low"
