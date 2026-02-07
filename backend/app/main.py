import os
import psycopg2
from fastapi import FastAPI

app = FastAPI(title="SRCI")

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