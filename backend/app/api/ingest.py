import os
from fastapi import APIRouter
from app.ingestion.service_ingestor import ingest_services
from app.ingestion.dependency_ingestor import ingest_dependencies

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL", "")

@router.post("/ingest")
def ingest_router():
    ingest_services(DATABASE_URL)
    ingest_dependencies(DATABASE_URL)
    return {"status": "ingest pipeline invoked"}