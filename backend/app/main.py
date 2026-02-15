import os
import psycopg2
from fastapi import FastAPI
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
from app.api.explain import router as explain_router
from app.api.reasoning import router as reasoning_router
from app.api.features import router as features_router
from app.api.train import router as train_router
from app.api.predict import router as predict_router

app = FastAPI(title="SRCI")

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
app.include_router(explain_router)
app.include_router(reasoning_router)
app.include_router(features_router)
app.include_router(train_router)
app.include_router(predict_router)

DATABASE_URL = os.getenv("DATABASE_URL")

def check_db():
    conn = psycopg2.connect(DATABASE_URL)
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
    return {"message": "SRCI backend running"}