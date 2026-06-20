import psycopg2

from app.autonomy.rca_runner import (
    RcaCircuitOpenError,
    RcaInProgressError,
    RcaRunnerError,
    run_rca_for_incident,
)


def run_rca_batch(db_url: str, limit: int = 10, dry_run: bool = False) -> dict:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id
        FROM incidents
        WHERE auto_rca_processed = FALSE
          AND auto_rca_in_progress = FALSE
        ORDER BY started_at DESC
        LIMIT %s
        """,
        (limit,),
    )
    incident_ids = [str(row[0]) for row in cur.fetchall()]
    cur.close()
    conn.close()

    if dry_run:
        return {
            "dry_run": True,
            "candidate_count": len(incident_ids),
            "incident_ids": incident_ids,
        }

    succeeded = []
    failed = []
    skipped = []

    for incident_id in incident_ids:
        try:
            result = run_rca_for_incident(db_url, incident_id)
            succeeded.append(
                {
                    "incident_id": incident_id,
                    "status": result.get("status"),
                    "quality_band": result.get("quality", {}).get("quality_band"),
                }
            )
        except RcaInProgressError as exc:
            skipped.append({"incident_id": incident_id, "reason": str(exc)})
        except (RcaCircuitOpenError, RcaRunnerError) as exc:
            failed.append({"incident_id": incident_id, "error": str(exc)})

    return {
        "dry_run": False,
        "total": len(incident_ids),
        "succeeded_count": len(succeeded),
        "failed_count": len(failed),
        "skipped_count": len(skipped),
        "succeeded": succeeded,
        "failed": failed,
        "skipped": skipped,
    }
