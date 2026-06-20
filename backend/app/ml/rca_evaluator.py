import psycopg2

from app.ml.predictor import predict_for_incident


def _precision_at_k(ranked_ids: list, positives: set, k: int) -> float:
    if k <= 0 or not ranked_ids:
        return 0.0
    top_k = ranked_ids[:k]
    hits = sum(1 for cid in top_k if cid in positives)
    return hits / min(k, len(top_k))


def _mean_reciprocal_rank(ranked_ids: list, positives: set) -> float:
    for i, cid in enumerate(ranked_ids, start=1):
        if cid in positives:
            return 1.0 / i
    return 0.0


def evaluate_rca_for_incident(db_url: str, incident_id: str) -> dict:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT change_id, label
        FROM incident_change_features
        WHERE incident_id = %s
        """,
        (incident_id,),
    )
    label_rows = cur.fetchall()
    cur.close()
    conn.close()

    if not label_rows:
        raise ValueError(f"No feature rows for incident {incident_id}")

    positives = {str(row[0]) for row in label_rows if row[1] == 1}
    labeled = {str(row[0]): row[1] for row in label_rows}

    if not positives:
        raise ValueError(
            "No positive labels (label=1) assigned — use POST /incidents/{id}/labels"
        )

    prediction_result = predict_for_incident(db_url, incident_id)
    predictions = prediction_result.get("predictions", [])
    ranked_ids = [str(p["change_id"]) for p in predictions]

    top1_hit = bool(ranked_ids and ranked_ids[0] in positives)
    mrr = _mean_reciprocal_rank(ranked_ids, positives)

    metrics = {
        "top1_hit": top1_hit,
        "mean_reciprocal_rank": round(mrr, 4),
        "precision_at_1": round(_precision_at_k(ranked_ids, positives, 1), 4),
        "precision_at_3": round(_precision_at_k(ranked_ids, positives, 3), 4),
        "positive_count": len(positives),
        "candidate_count": len(ranked_ids),
        "labeled_count": len(labeled),
    }

    return {
        "incident_id": incident_id,
        "metrics": metrics,
        "ground_truth": [
            {"change_id": cid, "label": lbl} for cid, lbl in labeled.items()
        ],
        "predictions": [
            {
                "change_id": str(p["change_id"]),
                "hybrid_score": p["hybrid_score"],
                "confidence_band": p.get("confidence_band"),
                "is_positive": str(p["change_id"]) in positives,
            }
            for p in predictions
        ],
    }
