import psycopg2
import numpy as np
import joblib
from collections import defaultdict

from app.config.scoring_weights import GRAPH_PENALTY_FACTOR, ML_WEIGHT, RULE_WEIGHT
from app.ingestion.evidence_linker import format_change_evidence_reference
from app.reasoning.hybrid_scorer import compute_hybrid_score
from app.reasoning.confidence_band import compute_confidence_band
from app.reasoning.rca_guardrails import validate_predictions

MODEL_PATH = "app/ml/model.joblib"


def predict_for_incident(db_url: str, incident_id: str):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    model = joblib.load(MODEL_PATH)

    cur.execute(
        """
        SELECT f.change_id,
               f.temporal_proximity,
               f.service_overlap,
               f.graph_distance,
               f.criticality_score,
               c.description,
               c.created_at,
               c.git_ref
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

    cur.execute("SELECT COUNT(*) FROM incident_change_features")
    ml_sample_count = cur.fetchone()[0]

    change_ids = [row[0] for row in rows]

    cur.execute(
        """
        SELECT change_id, confidence
        FROM root_cause_hypotheses
        WHERE incident_id = %s AND change_id = ANY(%s::uuid[])
        """,
        (incident_id, change_ids),
    )
    rule_confidence_map = {row[0]: float(row[1]) for row in cur.fetchall()}

    references = []
    ref_to_change = {}
    for row in rows:
        change_id, _, _, _, _, _, created_at, git_ref = row
        if git_ref and created_at:
            ref = format_change_evidence_reference(git_ref, created_at)
            references.append(ref)
            ref_to_change[ref] = change_id

    evidence_counts = defaultdict(int)
    if references:
        cur.execute(
            """
            SELECT reference, COUNT(*)
            FROM evidence
            WHERE incident_id = %s
              AND source_type = 'change'
              AND reference = ANY(%s)
            GROUP BY reference
            """,
            (incident_id, references),
        )
        for ref, count in cur.fetchall():
            evidence_counts[ref_to_change[ref]] = count

    predictions = []

    for row in rows:
        (
            change_id,
            temporal_proximity,
            service_overlap,
            graph_distance,
            criticality_score,
            change_description,
            change_created_at,
            _git_ref,
        ) = row

        temporal_proximity = float(temporal_proximity)
        service_overlap = float(service_overlap)
        graph_distance = int(graph_distance)
        criticality_score = float(criticality_score)
        change_created_at = (
            change_created_at.isoformat() if change_created_at else None
        )

        features = np.array(
            [
                temporal_proximity,
                service_overlap,
                graph_distance,
                criticality_score,
            ]
        ).reshape(1, -1)

        ml_probability = float(model.predict_proba(features)[0][1])
        rule_confidence = rule_confidence_map.get(change_id, 0.0)
        evidence_count = evidence_counts.get(change_id, 0)

        hybrid_score = compute_hybrid_score(
            rule_confidence,
            ml_probability,
            ml_sample_count=ml_sample_count,
            evidence_count=evidence_count,
        )

        graph_penalty = 0.0
        if graph_distance > 1:
            graph_penalty = -GRAPH_PENALTY_FACTOR * hybrid_score
            hybrid_score = max(0.0, hybrid_score + graph_penalty)

        hybrid_score = max(0.0, min(1.0, hybrid_score))
        confidence_band = compute_confidence_band(hybrid_score)

        decision_trace = {
            "weights": {
                "rule_weight": RULE_WEIGHT,
                "ml_weight": ML_WEIGHT,
                "calibrated": True,
            },
            "components": {
                "rule_confidence": round(rule_confidence, 6),
                "ml_probability": round(ml_probability, 6),
                "evidence_count": evidence_count,
                "ml_sample_count": ml_sample_count,
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

    predictions.sort(key=lambda x: x["hybrid_score"], reverse=True)
    predictions = validate_predictions(predictions)
    cur.close()
    conn.close()

    return {
        "incident_id": incident_id,
        "predictions": predictions,
    }
