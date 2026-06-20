import time
import uuid

from app.autonomy.rca_runner import run_rca_for_incident
from app.db import get_connection
from app.enterprise.sla import get_tenant_sla_target, record_sla_event
from app.ingestion.change_ingestor import ingest_change
from app.ingestion.incident_ingestor import ingest_incident


def run_chaos_scenario(
    db_url: str,
    tenant_id: str,
    scenario: str = "deployment_correlation",
) -> dict:
    run_id = str(uuid.uuid4())
    conn = get_connection(tenant_id=tenant_id)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO chaos_runs (id, tenant_id, scenario, status, injected_failure)
        VALUES (%s, %s, %s, 'running', %s)
        """,
        (run_id, tenant_id, scenario, f"synthetic_{scenario}"),
    )
    conn.commit()
    cur.close()
    conn.close()

    start = time.time()
    result = {"scenario": scenario, "steps": []}

    try:
        change_id = ingest_change(
            db_url,
            change_type="code",
            description=f"[CHAOS] Synthetic change for {scenario}",
            git_ref=f"chaos-{run_id[:8]}",
            services_touched=["payment-service"],
            tenant_id=tenant_id,
        )
        result["steps"].append({"step": "inject_change", "change_id": str(change_id)})

        incident_id = ingest_incident(
            db_url,
            title=f"[CHAOS] Synthetic incident — {scenario}",
            severity="high",
            started_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            affected_services=["payment-service"],
            tenant_id=tenant_id,
        )
        result["steps"].append({"step": "inject_incident", "incident_id": str(incident_id)})

        target = get_tenant_sla_target(tenant_id)
        record_sla_event(tenant_id, str(incident_id), "detected", target_minutes=target)
        record_sla_event(tenant_id, str(incident_id), "rca_started", target_minutes=target)

        rca_result = run_rca_for_incident(db_url, str(incident_id))
        result["steps"].append({"step": "run_rca", "status": rca_result.get("status")})

        record_sla_event(tenant_id, str(incident_id), "rca_completed", target_minutes=target)

        conn = get_connection(tenant_id=tenant_id)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT change_id FROM root_cause_hypotheses
            WHERE incident_id = %s
            ORDER BY confidence DESC NULLS LAST
            LIMIT 1
            """,
            (str(incident_id),),
        )
        top_row = cur.fetchone()
        actual_change_id = str(top_row[0]) if top_row and top_row[0] else None
        accuracy = 1.0 if actual_change_id == str(change_id) else 0.0
        passed = accuracy == 1.0
        duration_ms = int((time.time() - start) * 1000)

        cur.execute(
            """
            UPDATE chaos_runs
            SET status = %s, expected_rca_change_id = %s, actual_top_change_id = %s,
                rca_accuracy = %s, duration_ms = %s, result = %s::jsonb,
                completed_at = NOW()
            WHERE id = %s
            """,
            (
                "passed" if passed else "failed",
                change_id,
                actual_change_id,
                accuracy,
                duration_ms,
                __import__("json").dumps(result),
                run_id,
            ),
        )
        conn.commit()
        cur.close()
        conn.close()

        return {
            "run_id": run_id,
            "status": "passed" if passed else "failed",
            "rca_accuracy": accuracy,
            "expected_change_id": str(change_id),
            "actual_top_change_id": actual_change_id,
            "duration_ms": duration_ms,
            "steps": result["steps"],
        }
    except Exception as exc:
        duration_ms = int((time.time() - start) * 1000)
        conn = get_connection(tenant_id=tenant_id)
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE chaos_runs
            SET status = 'failed', duration_ms = %s, result = %s::jsonb, completed_at = NOW()
            WHERE id = %s
            """,
            (
                duration_ms,
                __import__("json").dumps({**result, "error": str(exc)}),
                run_id,
            ),
        )
        conn.commit()
        cur.close()
        conn.close()
        return {
            "run_id": run_id,
            "status": "failed",
            "error": str(exc),
            "duration_ms": duration_ms,
        }


def get_chaos_history(tenant_id: str, limit: int = 20) -> list:
    conn = get_connection(tenant_id=tenant_id)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, scenario, status, rca_accuracy, duration_ms, created_at, completed_at
        FROM chaos_runs
        WHERE tenant_id = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (tenant_id, limit),
    )
    rows = [
        {
            "id": str(r[0]),
            "scenario": r[1],
            "status": r[2],
            "rca_accuracy": float(r[3]) if r[3] is not None else None,
            "duration_ms": r[4],
            "created_at": r[5].isoformat(),
            "completed_at": r[6].isoformat() if r[6] else None,
        }
        for r in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return rows
