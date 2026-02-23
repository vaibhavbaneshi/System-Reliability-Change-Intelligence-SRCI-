import psycopg2
import numpy as np
import joblib

from app.reasoning.hybrid_scorer import compute_hybrid_score
from app.reasoning.confidence_band import compute_confidence_band
from app.reasoning.rca_guardrails import validate_predictions

MODEL_PATH = "app/ml/model.joblib"


def predict_for_incident(db_url: str, incident_id: str):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # -----------------------------
    # Load trained model
    # -----------------------------
    model = joblib.load(MODEL_PATH)

    # -----------------------------
    # Fetch ML features + change info
    # -----------------------------
    cur.execute(
        """
        SELECT f.change_id,
               f.temporal_proximity,
               f.service_overlap,
               f.graph_distance,
               f.criticality_score,
               c.description,
               c.created_at
        FROM incident_change_features f
        LEFT JOIN changes c ON f.change_id = c.id
        WHERE f.incident_id = %s
        """,
        (incident_id,),
    )

    rows = cur.fetchall()

    if not rows:
        cur.close()
        conn.close()
        return {
            "incident_id": incident_id,
            "predictions": [],
            "note": "No features found for this incident",
        }

    predictions = []

    # =============================
    # Score each candidate change
    # =============================
    for row in rows:
        change_id = row[0]
        temporal_proximity = float(row[1])
        service_overlap = float(row[2])
        graph_distance = int(row[3])
        criticality_score = float(row[4])
        change_description = row[5]
        change_created_at = (
            row[6].isoformat() if row[6] else None
        )

        # -----------------------------
        # ML probability
        # -----------------------------
        features = np.array(
            [
                temporal_proximity,
                service_overlap,
                graph_distance,
                criticality_score,
            ]
        ).reshape(1, -1)

        ml_probability = float(model.predict_proba(features)[0][1])

        # -----------------------------
        # Rule confidence
        # -----------------------------
        cur.execute(
            """
            SELECT confidence
            FROM root_cause_hypotheses
            WHERE incident_id = %s
              AND change_id = %s
            LIMIT 1
            """,
            (incident_id, change_id),
        )

        rc_row = cur.fetchone()
        rule_confidence = float(rc_row[0]) if rc_row else 0.0

        # =============================
        # Hybrid scoring (expanded)
        # =============================
        RULE_WEIGHT = 0.6
        ML_WEIGHT = 0.4

        rule_component = RULE_WEIGHT * rule_confidence
        ml_component = ML_WEIGHT * ml_probability

        hybrid_score = rule_component + ml_component

        # Graph penalty logic
        graph_penalty = 0.0
        if graph_distance > 1:
            graph_penalty = -0.1 * hybrid_score
            hybrid_score = hybrid_score + graph_penalty

        # Clamp safety
        hybrid_score = max(0.0, min(1.0, hybrid_score))

        # Confidence band
        confidence_band = compute_confidence_band(hybrid_score)

        # =============================
        # Decision trace (FULL)
        # =============================
        decision_trace = {
            "weights": {
                "rule_weight": RULE_WEIGHT,
                "ml_weight": ML_WEIGHT,
            },
            "components": {
                "rule_component": round(rule_component, 6),
                "ml_component": round(ml_component, 6),
                "graph_penalty": round(graph_penalty, 6),
            },
            "feature_snapshot": {
                "temporal_proximity": temporal_proximity,
                "service_overlap": service_overlap,
                "graph_distance": graph_distance,
                "criticality_score": criticality_score,
            },
            "final_score": round(hybrid_score, 6),
        }

        predictions.append(
            {
                "change_id": change_id,
                "change_description": change_description,
                "change_created_at": change_created_at,
                "rule_confidence": rule_confidence,
                "ml_probability": ml_probability,
                "hybrid_score": hybrid_score,
                "confidence_band": confidence_band,
                "decision_trace": decision_trace,
            }
        )

    # -----------------------------
    # Sort by hybrid score
    # -----------------------------
    predictions.sort(key=lambda x: x["hybrid_score"], reverse=True)
    predictions = validate_predictions(predictions)
    cur.close()
    conn.close()

    return {
        "incident_id": incident_id,
        "predictions": predictions,
    }