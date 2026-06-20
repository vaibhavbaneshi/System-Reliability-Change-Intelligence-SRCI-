import os

from fastapi import APIRouter

from app.autonomy.config import AUTONOMY_ENABLED
from app.autonomy.monitor import get_monitor

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL", "")


@router.get("/autonomy/status")
def autonomy_status():
    monitor = get_monitor(DATABASE_URL)
    status = monitor.status()
    status["autonomy_enabled_env"] = AUTONOMY_ENABLED
    return status


@router.post("/autonomy/start")
def start_autonomy():
    monitor = get_monitor(DATABASE_URL)
    if monitor.running:
        return {"status": "already_running", **monitor.status()}
    monitor.start()
    return {"status": "started", **monitor.status()}


@router.post("/autonomy/stop")
async def stop_autonomy():
    monitor = get_monitor(DATABASE_URL)
    if not monitor.running:
        return {"status": "already_stopped", **monitor.status()}
    await monitor.stop()
    return {"status": "stopped", **monitor.status()}
