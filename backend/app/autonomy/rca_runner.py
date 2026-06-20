import os
from datetime import datetime

import psycopg2

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


def _try_acquire_lock(conn, incident_id: str) -> bool:
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE incidents
        SET auto_rca_in_progress = TRUE,
            auto_rca_attempts = auto_rca_attempts + 1
        WHERE id = %s
          AND auto_rca_in_progress = FALSE
        RETURNING id
        """,
        (incident_id,),
    )
    acquired = cur.fetchone() is not None
    conn.commit()
    cur.close()
    return acquired


def _mark_success(conn, incident_id: str):
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE incidents
        SET auto_rca_processed = TRUE,
            auto_rca_processed_at = NOW(),
            auto_rca_in_progress = FALSE,
            auto_rca_last_error = NULL
        WHERE id = %s
        """,
        (incident_id,),
    )
    conn.commit()
    cur.close()


def _mark_failure(conn, incident_id: str, error_message: str):
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE incidents
        SET auto_rca_in_progress = FALSE,
            auto_rca_last_error = %s
        WHERE id = %s
        """,
        (error_message[:2000], incident_id),
    )
    conn.commit()
    cur.close()


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

    if not _try_acquire_lock(conn, incident_id):
        conn.close()
        raise RcaInProgressError(
            f"RCA already in progress for incident {incident_id}"
        )

    steps_completed = []

    try:
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

        _mark_success(conn, incident_id)
        rca_circuit_breaker.record_success()

        return {
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
            "processed_at": datetime.utcnow().isoformat() + "Z",
        }

    except Exception as exc:
        _mark_failure(conn, incident_id, str(exc))
        rca_circuit_breaker.record_failure()
        raise RcaRunnerError(str(exc)) from exc

    finally:
        conn.close()
