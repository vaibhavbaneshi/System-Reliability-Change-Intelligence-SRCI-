import psycopg2


def _classify_error(error_message: str) -> str:
    if not error_message:
        return "none"
    lower = error_message.lower()
    if "circuit breaker" in lower:
        return "circuit_open"
    if "already in progress" in lower or "in progress" in lower:
        return "lock_conflict"
    if "not found" in lower:
        return "not_found"
    if "training data" in lower or "model" in lower:
        return "model_error"
    if "no features" in lower:
        return "missing_features"
    return "step_failure"


def _recommendations(classification: str, attempts: int) -> list:
    recs = []
    if classification == "circuit_open":
        recs.append("Wait for circuit breaker cooldown before retrying")
    elif classification == "lock_conflict":
        recs.append("Another RCA run is active; retry after it completes")
    elif classification == "missing_features":
        recs.append("Run correlate and features steps before predict")
    elif classification == "model_error":
        recs.append("Assign labels and run POST /train to build the ML model")
    elif classification == "step_failure":
        recs.append("Inspect auto_rca_last_error and retry run-rca")
    if attempts >= 3:
        recs.append("High attempt count — consider manual investigation")
    if not recs:
        recs.append("No action required")
    return recs


def analyze_rca_failure(db_url: str, incident_id: str) -> dict:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT auto_rca_processed,
               auto_rca_attempts,
               auto_rca_last_error,
               auto_rca_in_progress,
               auto_rca_processed_at
        FROM incidents
        WHERE id = %s
        """,
        (incident_id,),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row is None:
        raise ValueError(f"Incident {incident_id} not found")

    processed, attempts, last_error, in_progress, processed_at = row
    classification = _classify_error(last_error or "")

    if processed and not last_error:
        status = "success"
    elif in_progress:
        status = "in_progress"
    elif last_error:
        status = "failed"
    else:
        status = "not_processed"

    return {
        "incident_id": incident_id,
        "status": status,
        "failure_detected": bool(last_error),
        "classification": classification,
        "attempts": attempts or 0,
        "last_error": last_error,
        "in_progress": bool(in_progress),
        "processed_at": processed_at.isoformat() if processed_at else None,
        "recommendations": _recommendations(classification, attempts or 0),
    }
