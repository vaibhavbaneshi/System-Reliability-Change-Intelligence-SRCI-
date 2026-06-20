import os

from app.config.scoring_weights import ML_WEIGHT, RULE_WEIGHT
from app.db import get_connection
from app.ml.predictor import predict_for_incident
from app.reasoning.hybrid_scorer import compute_hybrid_score

CANARY_ML_WEIGHT = float(os.getenv("SRCI_CANARY_ML_WEIGHT", str(ML_WEIGHT + 0.05)))
CANARY_RULE_WEIGHT = float(os.getenv("SRCI_CANARY_RULE_WEIGHT", str(RULE_WEIGHT - 0.05)))
DIVERGENCE_THRESHOLD = float(os.getenv("SRCI_CANARY_DIVERGENCE_THRESHOLD", "0.15"))
DATABASE_URL = os.getenv("DATABASE_URL", "")


def run_canary_scoring(tenant_id: str, incident_id: str) -> dict:
    prod = predict_for_incident(DATABASE_URL, incident_id)
    predictions = prod.get("predictions", [])

    conn = get_connection(tenant_id=tenant_id)
    cur = conn.cursor()
    results = []

    for pred in predictions:
        change_id = pred.get("change_id")
        rule = float(pred.get("rule_confidence", 0))
        ml = float(pred.get("ml_probability", 0))
        prod_score = float(pred.get("hybrid_score", 0))
        canary = compute_hybrid_score(
            rule,
            ml,
            ml_sample_count=pred.get("decision_trace", {})
            .get("components", {})
            .get("ml_sample_count", 0),
            evidence_count=pred.get("decision_trace", {})
            .get("components", {})
            .get("evidence_count", 0),
            base_rule_weight=CANARY_RULE_WEIGHT,
            base_ml_weight=CANARY_ML_WEIGHT,
        )
        delta = abs(canary - prod_score)
        diverged = delta >= DIVERGENCE_THRESHOLD

        cur.execute(
            """
            INSERT INTO canary_predictions
                (tenant_id, incident_id, change_id, production_score, canary_score,
                 score_delta, diverged)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (tenant_id, incident_id, change_id, prod_score, canary, delta, diverged),
        )
        results.append(
            {
                "id": str(cur.fetchone()[0]),
                "change_id": str(change_id) if change_id else None,
                "production_score": round(prod_score, 4),
                "canary_score": round(canary, 4),
                "score_delta": round(delta, 4),
                "diverged": diverged,
            }
        )

    conn.commit()
    cur.close()
    conn.close()

    diverged_count = sum(1 for r in results if r["diverged"])
    return {
        "incident_id": incident_id,
        "predictions": results,
        "diverged_count": diverged_count,
        "canary_weights": {"rule": CANARY_RULE_WEIGHT, "ml": CANARY_ML_WEIGHT},
    }


def get_canary_history(tenant_id: str, limit: int = 50) -> list:
    conn = get_connection(tenant_id=tenant_id)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, incident_id, change_id, production_score, canary_score,
               score_delta, diverged, created_at
        FROM canary_predictions
        WHERE tenant_id = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (tenant_id, limit),
    )
    rows = [
        {
            "id": str(r[0]),
            "incident_id": str(r[1]),
            "change_id": str(r[2]) if r[2] else None,
            "production_score": float(r[3]) if r[3] is not None else None,
            "canary_score": float(r[4]) if r[4] is not None else None,
            "score_delta": float(r[5]) if r[5] is not None else None,
            "diverged": r[6],
            "created_at": r[7].isoformat(),
        }
        for r in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return rows
