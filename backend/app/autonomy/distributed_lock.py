from app.autonomy.config import LOCK_STALE_MINUTES


def acquire_rca_lock(conn, incident_id: str) -> bool:
    """
    DB-backed lock with stale-lock recovery for multi-worker deployments.
    """
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE incidents
        SET auto_rca_in_progress = TRUE,
            auto_rca_attempts = auto_rca_attempts + 1,
            auto_rca_locked_at = NOW()
        WHERE id = %s
          AND (
            auto_rca_in_progress = FALSE
            OR auto_rca_locked_at IS NULL
            OR auto_rca_locked_at < NOW() - (%s * INTERVAL '1 minute')
          )
        RETURNING id
        """,
        (incident_id, LOCK_STALE_MINUTES),
    )
    acquired = cur.fetchone() is not None
    conn.commit()
    cur.close()
    return acquired


def release_rca_lock_success(conn, incident_id: str):
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE incidents
        SET auto_rca_processed = TRUE,
            auto_rca_processed_at = NOW(),
            auto_rca_in_progress = FALSE,
            auto_rca_locked_at = NULL,
            auto_rca_last_error = NULL
        WHERE id = %s
        """,
        (incident_id,),
    )
    conn.commit()
    cur.close()


def release_rca_lock_failure(conn, incident_id: str, error_message: str):
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE incidents
        SET auto_rca_in_progress = FALSE,
            auto_rca_locked_at = NULL,
            auto_rca_last_error = %s
        WHERE id = %s
        """,
        (error_message[:2000], incident_id),
    )
    conn.commit()
    cur.close()
