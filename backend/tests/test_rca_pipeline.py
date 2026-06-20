"""
Integration tests for the orchestrated RCA pipeline.
Run: cd backend && PYTHONPATH=. pytest tests/ -v
Requires: Postgres with srci database and demo data (scripts/setup_demo.sh).
"""

import os
import uuid

import pytest

pytest.importorskip("psycopg2")

from app.autonomy.rca_runner import RcaInProgressError, run_rca_for_incident

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://srci:srci@localhost:5432/srci"
)


@pytest.fixture
def incident_id():
    ids_file = os.path.join(
        os.path.dirname(__file__), "..", "..", ".demo_ids"
    )
    if os.path.isfile(ids_file):
        env = {}
        with open(ids_file) as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    env[k] = v
        if env.get("INCIDENT_ID"):
            return env["INCIDENT_ID"]
    pytest.skip("No demo incident — run scripts/setup_demo.sh first")


def test_run_rca_completes(incident_id):
    result = run_rca_for_incident(DATABASE_URL, incident_id)
    assert result["status"] == "completed"
    assert "correlate" in result["steps_completed"]
    assert "predict" in result["steps_completed"]
    assert "explain" in result["steps_completed"]
    assert result.get("explanation")


def test_run_rca_rejects_unknown_incident():
    fake_id = str(uuid.uuid4())
    with pytest.raises(Exception) as exc:
        run_rca_for_incident(DATABASE_URL, fake_id)
    assert "not found" in str(exc.value).lower()


def test_run_rca_rejects_concurrent_run(incident_id):
    import psycopg2

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE incidents SET auto_rca_in_progress = TRUE WHERE id = %s
        """,
        (incident_id,),
    )
    conn.commit()
    cur.close()
    conn.close()

    try:
        with pytest.raises(RcaInProgressError):
            run_rca_for_incident(DATABASE_URL, incident_id)
    finally:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            "UPDATE incidents SET auto_rca_in_progress = FALSE WHERE id = %s",
            (incident_id,),
        )
        conn.commit()
        cur.close()
        conn.close()
