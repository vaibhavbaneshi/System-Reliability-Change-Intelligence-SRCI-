import os


def _float_env(name: str, default: float) -> float:
    return float(os.getenv(name, str(default)))


def _int_env(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


RULE_WEIGHT = _float_env("SRCI_RULE_WEIGHT", 0.6)
ML_WEIGHT = _float_env("SRCI_ML_WEIGHT", 0.4)

IMPACT_WEIGHTS = {
    "high": _float_env("SRCI_IMPACT_WEIGHT_HIGH", 0.7),
    "medium": _float_env("SRCI_IMPACT_WEIGHT_MEDIUM", 0.4),
    "low": _float_env("SRCI_IMPACT_WEIGHT_LOW", 0.2),
}

CRITICALITY_WEIGHTS = {
    "high": 1.0,
    "medium": 0.6,
    "low": 0.3,
}

EVIDENCE_BOOST_PER_ITEM = _float_env("SRCI_EVIDENCE_BOOST", 0.1)
EVIDENCE_BOOST_MAX = _float_env("SRCI_EVIDENCE_BOOST_MAX", 0.2)

WEAK_SIGNAL_THRESHOLD = _float_env("SRCI_WEAK_SIGNAL_THRESHOLD", 0.55)
CLOSE_COMPETITION_DELTA = _float_env("SRCI_CLOSE_COMPETITION_DELTA", 0.08)
ESCALATION_HYBRID_THRESHOLD = _float_env("SRCI_ESCALATION_THRESHOLD", 0.55)

CONFIDENCE_BAND_HIGH = _float_env("SRCI_CONFIDENCE_BAND_HIGH", 0.75)
CONFIDENCE_BAND_MEDIUM = _float_env("SRCI_CONFIDENCE_BAND_MEDIUM", 0.5)

GRAPH_PENALTY_FACTOR = _float_env("SRCI_GRAPH_PENALTY_FACTOR", 0.1)
TEMPORAL_WINDOW_HOURS = _int_env("SRCI_TEMPORAL_WINDOW_HOURS", 24)

ML_RELIABILITY_SMALL = _float_env("SRCI_ML_RELIABILITY_SMALL", 0.4)
ML_RELIABILITY_MEDIUM = _float_env("SRCI_ML_RELIABILITY_MEDIUM", 0.7)
ML_SAMPLE_SMALL = _int_env("SRCI_ML_SAMPLE_SMALL", 10)
ML_SAMPLE_MEDIUM = _int_env("SRCI_ML_SAMPLE_MEDIUM", 50)

RULE_RELIABILITY_NONE = _float_env("SRCI_RULE_RELIABILITY_NONE", 0.6)
RULE_RELIABILITY_ONE = _float_env("SRCI_RULE_RELIABILITY_ONE", 0.8)
