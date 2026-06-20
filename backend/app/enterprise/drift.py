import statistics
from datetime import datetime, timedelta, timezone

from app.db import get_connection

DRIFT_THRESHOLD = 2.0  # z-score threshold


def compute_drift(tenant_id: str, window_hours: int = 24) -> dict:
    conn = get_connection(tenant_id=tenant_id)
    cur = conn.cursor()
    window_end = datetime.now(timezone.utc)
    window_start = window_end - timedelta(hours=window_hours)

    cur.execute(
        """
        SELECT
            icf.temporal_proximity,
            icf.service_overlap,
            icf.graph_distance
        FROM incident_change_features icf
        JOIN incidents i ON i.id = icf.incident_id
        WHERE i.tenant_id = %s
          AND icf.created_at >= %s
        """,
        (tenant_id, window_start),
    )
    rows = cur.fetchall()

    features = {
        "temporal_proximity": [r[0] for r in rows if r[0] is not None],
        "service_overlap": [r[1] for r in rows if r[1] is not None],
        "graph_distance": [r[2] for r in rows if r[2] is not None],
    }

    snapshots = []
    drift_detected_any = False

    for name, values in features.items():
        if len(values) < 3:
            continue
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values) if len(values) > 1 else 0.0

        cur.execute(
            """
            SELECT mean_value, std_value FROM drift_snapshots
            WHERE tenant_id = %s AND feature_name = %s
            ORDER BY created_at DESC LIMIT 1
            """,
            (tenant_id, name),
        )
        baseline = cur.fetchone()
        baseline_mean = float(baseline[0]) if baseline else mean_val
        baseline_std = float(baseline[1]) if baseline and baseline[1] else max(std_val, 0.01)

        drift_score = abs(mean_val - baseline_mean) / baseline_std if baseline_std else 0.0
        drift_detected = drift_score >= DRIFT_THRESHOLD
        if drift_detected:
            drift_detected_any = True

        cur.execute(
            """
            INSERT INTO drift_snapshots
                (tenant_id, feature_name, mean_value, std_value, sample_count,
                 baseline_mean, baseline_std, drift_score, drift_detected,
                 window_start, window_end)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                tenant_id,
                name,
                mean_val,
                std_val,
                len(values),
                baseline_mean,
                baseline_std,
                drift_score,
                drift_detected,
                window_start,
                window_end,
            ),
        )
        snap_id = cur.fetchone()[0]
        snapshots.append(
            {
                "id": str(snap_id),
                "feature_name": name,
                "mean_value": round(mean_val, 4),
                "baseline_mean": round(baseline_mean, 4),
                "drift_score": round(drift_score, 4),
                "drift_detected": drift_detected,
                "sample_count": len(values),
            }
        )

    conn.commit()
    cur.close()
    conn.close()

    return {
        "window_hours": window_hours,
        "drift_detected": drift_detected_any,
        "features": snapshots,
    }


def get_drift_history(tenant_id: str, limit: int = 50) -> list:
    conn = get_connection(tenant_id=tenant_id)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, feature_name, mean_value, baseline_mean, drift_score,
               drift_detected, sample_count, created_at
        FROM drift_snapshots
        WHERE tenant_id = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (tenant_id, limit),
    )
    rows = [
        {
            "id": str(r[0]),
            "feature_name": r[1],
            "mean_value": float(r[2]) if r[2] is not None else None,
            "baseline_mean": float(r[3]) if r[3] is not None else None,
            "drift_score": float(r[4]) if r[4] is not None else None,
            "drift_detected": r[5],
            "sample_count": r[6],
            "created_at": r[7].isoformat(),
        }
        for r in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return rows
