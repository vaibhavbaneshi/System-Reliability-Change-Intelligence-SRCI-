import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.autonomy.config import AUTONOMY_ENABLED
from app.autonomy.monitor import get_monitor
from app.auth.middleware import AuthMiddleware
from app.api.ingest import router as ingest_router
from app.api.services import router as services_router
from app.api.dependencies import router as dependencies_router
from app.api.changes import router as changes_router
from app.api.impact import router as impact_router
from app.api.changes_read import router as changes_read_router
from app.api.change_detail import router as change_detail_router
from app.api.change_impact import router as change_impact_router
from app.api.incidents import router as incidents_router
from app.api.correlation import router as correlate_incident
from app.api.hypotheses import router as hypotheses_router
from app.api.evidence import router as evidence_router
from app.api.evidence_read import router as evidence_read_router
from app.api.explain import router as explain_router
from app.api.reasoning import router as reasoning_router
from app.api.features import router as features_router
from app.api.train import router as train_router
from app.api.predict import router as predict_router
from app.api.rca import router as rca_router
from app.api.labels import router as labels_router
from app.api.evaluate import router as evaluate_router
from app.api.batch import router as batch_router
from app.api.rca_failure import router as rca_failure_router
from app.api.autonomy import router as autonomy_router
from app.api.feedback import router as feedback_router
from app.api.metrics import router as metrics_router
from app.api.incidents_read import router as incidents_read_router
from app.api.chat import router as chat_router
from app.api.auth_routes import router as auth_router
from app.api.sla_routes import router as sla_router
from app.api.enterprise_routes import router as enterprise_router
from app.api.graph_routes import router as graph_router
from app.api.git_routes import router as git_router, webhook_router
from app.db import get_bypass_connection

DATABASE_URL = os.getenv("DATABASE_URL")


@asynccontextmanager
async def lifespan(app: FastAPI):
    monitor = get_monitor(DATABASE_URL or "")
    if AUTONOMY_ENABLED:
        monitor.start()
    yield
    if monitor.running:
        await monitor.stop()


app = FastAPI(title="SRCI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(
        "SRCI_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)

app.include_router(auth_router)
app.include_router(sla_router)
app.include_router(enterprise_router)
app.include_router(graph_router)
app.include_router(git_router)
app.include_router(webhook_router)
app.include_router(ingest_router)
app.include_router(services_router)
app.include_router(dependencies_router)
app.include_router(changes_router)
app.include_router(impact_router)
app.include_router(changes_read_router)
app.include_router(change_detail_router)
app.include_router(change_impact_router)
app.include_router(incidents_router)
app.include_router(correlate_incident)
app.include_router(hypotheses_router)
app.include_router(evidence_router)
app.include_router(evidence_read_router)
app.include_router(explain_router)
app.include_router(reasoning_router)
app.include_router(features_router)
app.include_router(train_router)
app.include_router(predict_router)
app.include_router(rca_router)
app.include_router(labels_router)
app.include_router(evaluate_router)
app.include_router(batch_router)
app.include_router(rca_failure_router)
app.include_router(autonomy_router)
app.include_router(feedback_router)
app.include_router(metrics_router)
app.include_router(incidents_read_router)
app.include_router(chat_router)


def check_db():
    conn = get_bypass_connection()
    conn.close()


@app.get("/health")
def health():
    try:
        check_db()
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "error", "db": str(e)}


@app.get("/")
def root():
    return {"message": "SRCI backend running", "phase": "17-enterprise"}
