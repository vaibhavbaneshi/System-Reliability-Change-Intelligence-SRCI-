import json
import os
import urllib.error
import urllib.request

from app.autonomy.config import (
    DATADOG_WEBHOOK_URL,
    ESCALATION_WEBHOOK_URL,
    PAGERDUTY_ROUTING_KEY,
)


def _post_json(url: str, payload: dict, headers: dict = None) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, data=data, headers=req_headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return {"sent": True, "status_code": resp.status}
    except urllib.error.HTTPError as exc:
        return {"sent": False, "error": str(exc), "status_code": exc.code}
    except Exception as exc:
        return {"sent": False, "error": str(exc)}


def send_pagerduty_escalation(
    incident_id: str, escalation: dict, rca_summary: dict = None
) -> dict:
    if not PAGERDUTY_ROUTING_KEY:
        return {"channel": "pagerduty", "sent": False, "reason": "not_configured"}

    summary = f"SRCI weak RCA for incident {incident_id}"
    if rca_summary:
        desc = rca_summary.get("top_change_description") or "unknown change"
        score = rca_summary.get("hybrid_score", 0)
        summary = f"SRCI review required: {desc} (score {score:.3f})"

    payload = {
        "routing_key": PAGERDUTY_ROUTING_KEY,
        "event_action": "trigger",
        "payload": {
            "summary": summary,
            "severity": "warning",
            "source": "srci",
            "custom_details": {
                "incident_id": incident_id,
                "escalation": escalation,
                "rca_summary": rca_summary,
            },
        },
    }
    result = _post_json("https://events.pagerduty.com/v2/enqueue", payload)
    result["channel"] = "pagerduty"
    return result


def send_datadog_event(
    incident_id: str, escalation: dict, rca_summary: dict = None
) -> dict:
    if not DATADOG_WEBHOOK_URL:
        return {"channel": "datadog", "sent": False, "reason": "not_configured"}

    payload = {
        "title": f"SRCI escalation: incident {incident_id}",
        "text": json.dumps(
            {"escalation": escalation, "rca_summary": rca_summary}, default=str
        ),
        "alert_type": "warning",
        "source_type_name": "srci",
        "tags": [f"incident_id:{incident_id}"],
    }
    result = _post_json(DATADOG_WEBHOOK_URL, payload)
    result["channel"] = "datadog"
    return result


def send_generic_webhook(
    incident_id: str, escalation: dict, rca_summary: dict = None
) -> dict:
    url = ESCALATION_WEBHOOK_URL
    if not url:
        return {"channel": "webhook", "sent": False, "reason": "not_configured"}

    payload = {
        "event": "rca_escalation",
        "incident_id": incident_id,
        "escalation": escalation,
        "rca_summary": rca_summary,
    }
    result = _post_json(url, payload)
    result["channel"] = "webhook"
    return result


def dispatch_escalation_notifications(
    incident_id: str, escalation: dict, rca_summary: dict = None
) -> list:
    if not escalation or not escalation.get("should_escalate"):
        return []

    from app.autonomy.metrics import record_escalation

    record_escalation()

    results = [
        send_pagerduty_escalation(incident_id, escalation, rca_summary),
        send_datadog_event(incident_id, escalation, rca_summary),
        send_generic_webhook(incident_id, escalation, rca_summary),
    ]
    return results


def log_otel_span(incident_id: str, result: dict):
    """Lightweight trace hook when full OTel SDK is not installed."""
    if os.getenv("SRCI_OTEL_ENABLED", "false").lower() not in ("1", "true", "yes"):
        return
    span = {
        "trace": "srci.rca",
        "incident_id": incident_id,
        "status": result.get("status"),
        "quality_band": (result.get("quality") or {}).get("quality_band"),
        "escalated": (result.get("escalation") or {}).get("should_escalate"),
    }
    print(json.dumps(span))
