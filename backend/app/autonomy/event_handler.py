from app.autonomy.config import AUTO_RCA_ON_INGEST
from app.autonomy.worker_pool import get_worker_pool


def trigger_rca_on_ingest(db_url: str, incident_id: str) -> dict:
    if not AUTO_RCA_ON_INGEST:
        return {"triggered": False, "reason": "auto_rca_on_ingest_disabled"}

    pool = get_worker_pool(db_url)
    future = pool.submit(str(incident_id))
    return {
        "triggered": True,
        "incident_id": str(incident_id),
        "queued": not future.done(),
    }
