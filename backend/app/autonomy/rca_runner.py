import os
from datetime import datetime

import psycopg2

from app.autonomy.distributed_lock import (
    acquire_rca_lock,
    release_rca_lock_failure,
    release_rca_lock_success,
)
from app.autonomy.metrics import RcaTimer
from app.autonomy.notifications import (
    dispatch_escalation_notifications,
    log_otel_span,
)
from app.autonomy.safety import rca_circuit_breaker, with_retry
from app.ingestion.evidence_linker import link_change_evidence
from app.ingestion.incident_change_correlator import correlate_incident_to_changes
from app.ml.feature_builder import build_features_for_incident
from app.ml.predictor import predict_for_incident
from app.reasoning.explanation_builder import build_explanation_response


class RcaRunnerError(Exception):
    pass


class RcaInProgressError(RcaRunnerError):
    pass


class RcaCircuitOpenError(RcaRunnerError):
    pass


def _incident_exists(cur, incident_id: str) -> bool:
    cur.execute("SELECT id FROM incidents WHERE id = %s", (incident_id,))
    return cur.fetchone() is not None


def _ensure_model(db_url: str):
    model_path = os.path.join(
        os.getenv("SRCI_MODEL_DIR", "app/ml"),
        "model.joblib",
    )
    if os.path.isfile(model_path):
        return
    try:
        from app.ml.train_model import train_model

        train_model(db_url)
    except Exception:
        pass


def run_rca_for_incident(db_url: str, incident_id: str) -> dict:
    if rca_circuit_breaker.is_open():
        raise RcaCircuitOpenError(
            "RCA circuit breaker is open due to repeated failures"
        )

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    if not _incident_exists(cur, incident_id):
        cur.close()
        conn.close()
        raise RcaRunnerError(f"Incident {incident_id} not found")

    cur.close()

    if not acquire_rca_lock(conn, incident_id):
        conn.close()
        raise RcaInProgressError(
            f"RCA already in progress for incident {incident_id}"
        )

    steps_completed = []

    try:
        with RcaTimer():
            with_retry(correlate_incident_to_changes, db_url, incident_id)
            steps_completed.append("correlate")

            with_retry(build_features_for_incident, db_url, incident_id)
            steps_completed.append("features")

            with_retry(link_change_evidence, db_url, incident_id)
            steps_completed.append("evidence")

            with_retry(correlate_incident_to_changes, db_url, incident_id)
            steps_completed.append("re_correlate")

            _ensure_model(db_url)

            prediction_result = with_retry(predict_for_incident, db_url, incident_id)
            steps_completed.append("predict")

            explanation_result = build_explanation_response(
                db_url, incident_id, prediction_result
            )
            steps_completed.append("explain")

            release_rca_lock_success(conn, incident_id)
            rca_circuit_breaker.record_success()

            result = {
                "incident_id": incident_id,
                "status": "completed",
                "steps_completed": steps_completed,
                "hypotheses_found": len(explanation_result.get("predictions", [])),
                "predictions": explanation_result.get("predictions", []),
                "explanation": explanation_result.get("explanation"),
                "explanation_source": explanation_result.get("explanation_source"),
                "confidence": explanation_result.get("confidence"),
                "rca_summary": explanation_result.get("rca_summary"),
                "debug_trace": explanation_result.get("debug_trace"),
                "context_flags": explanation_result.get("context_flags"),
                "escalation": explanation_result.get("escalation"),
                "quality": explanation_result.get("quality"),
                "processed_at": datetime.utcnow().isoformat() + "Z",
            }

            escalation = result.get("escalation") or {}
            if escalation.get("should_escalate"):
                result["notifications"] = dispatch_escalation_notifications(
                    incident_id,
                    escalation,
                    result.get("rca_summary"),
                )

            log_otel_span(incident_id, result)
            return result

    except Exception as exc:
        release_rca_lock_failure(conn, incident_id, str(exc))
        rca_circuit_breaker.record_failure()
        raise RcaRunnerError(str(exc)) from exc

    finally:
        conn.close()
