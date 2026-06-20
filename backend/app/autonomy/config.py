import os


def _bool_env(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).lower() in ("1", "true", "yes")


AUTONOMY_ENABLED = _bool_env("SRCI_AUTONOMY_ENABLED", "false")
AUTO_RCA_ON_INGEST = _bool_env("SRCI_AUTO_RCA_ON_INGEST", "true")
POLL_INTERVAL_SEC = int(os.getenv("SRCI_POLL_INTERVAL_SEC", "30"))
POLL_BATCH_LIMIT = int(os.getenv("SRCI_POLL_BATCH_LIMIT", "5"))
RCA_WORKERS = int(os.getenv("SRCI_RCA_WORKERS", "2"))
LOCK_STALE_MINUTES = int(os.getenv("SRCI_LOCK_STALE_MINUTES", "10"))
LEARNING_LOOP_ENABLED = _bool_env("SRCI_LEARNING_LOOP_ENABLED", "true")
MIN_LABELS_FOR_RETRAIN = int(os.getenv("SRCI_MIN_LABELS_FOR_RETRAIN", "2"))

PAGERDUTY_ROUTING_KEY = os.getenv("PAGERDUTY_ROUTING_KEY", "")
DATADOG_WEBHOOK_URL = os.getenv("DATADOG_WEBHOOK_URL", "")
ESCALATION_WEBHOOK_URL = os.getenv("SRCI_ESCALATION_WEBHOOK_URL", "")
