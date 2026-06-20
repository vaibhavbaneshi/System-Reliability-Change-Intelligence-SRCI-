import asyncio
import logging
from typing import Optional

import psycopg2

from app.autonomy.batch_runner import run_rca_batch
from app.autonomy.config import POLL_BATCH_LIMIT, POLL_INTERVAL_SEC
from app.autonomy.metrics import set_active_workers, set_unprocessed_count
from app.autonomy.worker_pool import get_worker_pool

logger = logging.getLogger("srci.autonomy.monitor")


class AutonomyMonitor:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self._last_poll = None
        self._last_result = None

    @property
    def running(self) -> bool:
        return self._running

    def start(self):
        if self._running:
            return
        self._running = True
        loop = asyncio.get_event_loop()
        self._task = loop.create_task(self._poll_loop())
        logger.info("Autonomy monitor started (interval=%ss)", POLL_INTERVAL_SEC)

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        pool = get_worker_pool(self.db_url)
        pool.shutdown()
        logger.info("Autonomy monitor stopped")

    async def _poll_loop(self):
        while self._running:
            try:
                self._last_result = await asyncio.to_thread(self._poll_once)
                self._last_poll = asyncio.get_event_loop().time()
            except Exception as exc:
                logger.exception("Monitor poll failed: %s", exc)
            await asyncio.sleep(POLL_INTERVAL_SEC)

    def _poll_once(self) -> dict:
        unprocessed = self._count_unprocessed()
        set_unprocessed_count(unprocessed)

        pool = get_worker_pool(self.db_url)
        set_active_workers(pool.active_count())

        if unprocessed == 0:
            return {"polled": True, "processed": 0, "unprocessed": 0}

        result = run_rca_batch(
            self.db_url, limit=POLL_BATCH_LIMIT, dry_run=False
        )
        result["unprocessed_remaining"] = self._count_unprocessed()
        set_unprocessed_count(result["unprocessed_remaining"])
        return result

    def _count_unprocessed(self) -> int:
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COUNT(*)
            FROM incidents
            WHERE auto_rca_processed = FALSE
              AND auto_rca_in_progress = FALSE
            """
        )
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return count

    def status(self) -> dict:
        return {
            "running": self._running,
            "poll_interval_sec": POLL_INTERVAL_SEC,
            "poll_batch_limit": POLL_BATCH_LIMIT,
            "unprocessed_incidents": self._count_unprocessed(),
            "active_workers": get_worker_pool(self.db_url).active_count(),
            "last_poll": self._last_poll,
            "last_result": self._last_result,
        }


_monitor: Optional[AutonomyMonitor] = None


def get_monitor(db_url: str) -> AutonomyMonitor:
    global _monitor
    if _monitor is None:
        _monitor = AutonomyMonitor(db_url)
    return _monitor
