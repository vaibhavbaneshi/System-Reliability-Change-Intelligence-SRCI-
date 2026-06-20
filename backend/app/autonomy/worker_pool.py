import os
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Dict, Optional

from app.autonomy.config import RCA_WORKERS

_pool: Optional["RcaWorkerPool"] = None


class RcaWorkerPool:
    def __init__(self, db_url: str, max_workers: int = RCA_WORKERS):
        self.db_url = db_url
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="srci-rca",
        )
        self._active: Dict[str, Future] = {}

    def submit(self, incident_id: str) -> Future:
        from app.autonomy.rca_runner import run_rca_for_incident

        incident_id = str(incident_id)
        existing = self._active.get(incident_id)
        if existing and not existing.done():
            return existing

        future = self.executor.submit(
            run_rca_for_incident, self.db_url, incident_id
        )
        self._active[incident_id] = future
        future.add_done_callback(lambda _: self._active.pop(incident_id, None))
        return future

    def active_count(self) -> int:
        return sum(1 for f in self._active.values() if not f.done())

    def shutdown(self):
        self.executor.shutdown(wait=False)


def get_worker_pool(db_url: str = None) -> RcaWorkerPool:
    global _pool
    if _pool is None:
        url = db_url or os.getenv("DATABASE_URL", "")
        _pool = RcaWorkerPool(url)
    return _pool
