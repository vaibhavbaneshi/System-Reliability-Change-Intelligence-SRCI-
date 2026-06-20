import os
import psycopg2
from typing import Optional
from fastapi import HTTPException

from app.genai.explainer import generate_explanation
from app.ml.predictor import predict_for_incident
from app.reasoning.escalation import evaluate_escalation
from app.reasoning.rca_quality import compute_rca_quality
from app.reasoning.rca_guardrails import (
    detect_weak_signal,
    detect_close_competition,
)


def build_debug_trace(predictions: list):
    if not predictions:
        return {}

    top = predictions[0]
    runner_up = predictions[1] if len(predictions) > 1 else None

    feature_snapshot = top.get("decision_trace", {}).get("feature_snapshot", {})

    if runner_up:
        delta = top["hybrid_score"] - runner_up["hybrid_score"]
        why_text = f"Top candidate outranks next change by {delta:.3f} hybrid score."
    else:
        why_text = "Only candidate available for this incident."

    return {
        "ranking_factors": {
            "rule_weight": top.get("decision_trace", {})
            .get("weights", {})
            .get("rule_weight"),
            "ml_weight": top.get("decision_trace", {})
            .get("weights", {})
            .get("ml_weight"),
            "graph_penalty": top.get("decision_trace", {})
            .get("components", {})
            .get("graph_penalty"),
        },
        "feature_vector": feature_snapshot,
        "why_ranked_above_others": why_text,
        "competing_candidates": [
            {
                "change_id": c["change_id"],
                "hybrid_score": c["hybrid_score"],
                "confidence_band": c.get("confidence_band"),
            }
            for c in predictions[1:]
        ],
    }


def build_explanation_response(
    db_url: str,
    incident_id: str,
    prediction_result: Optional[dict] = None,
):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT title, severity, started_at
        FROM incidents
        WHERE id = %s
        """,
        (incident_id,),
    )
    incident = cur.fetchone()

    if incident is None:
        cur.close()
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Incident {incident_id} not found",
        )

    cur.execute(
        """
        SELECT s.id, s.name
        FROM incident_entities ie
        JOIN services s ON ie.entity_id = s.id
        WHERE ie.incident_id = %s
          AND ie.entity_type = 'service'
        """,
        (incident_id,),
    )
    services = cur.fetchall()

    cur.execute(
        """
        SELECT r.change_id, r.confidence, c.description, c.created_at
        FROM root_cause_hypotheses r
        LEFT JOIN changes c ON r.change_id = c.id
        WHERE r.incident_id = %s
        ORDER BY r.confidence DESC
        """,
        (incident_id,),
    )
    hypotheses_rows = cur.fetchall()

    cur.execute(
        """
        SELECT source_type, reference
        FROM evidence
        WHERE incident_id = %s
        """,
        (incident_id,),
    )
    evidence_rows = cur.fetchall()

    cur.close()
    conn.close()

    if prediction_result is None:
        prediction_result = predict_for_incident(db_url, incident_id)

    candidates = prediction_result.get("predictions", [])
    weak_signal = detect_weak_signal(candidates)
    close_competition = detect_close_competition(candidates)
    debug_trace = build_debug_trace(candidates)
    top_candidate = candidates[0] if candidates else None

    rca_summary = None
    if top_candidate:
        rca_summary = {
            "top_change_id": top_candidate.get("change_id"),
            "top_change_description": top_candidate.get("change_description"),
            "hybrid_score": top_candidate.get("hybrid_score"),
            "confidence_band": top_candidate.get("confidence_band"),
            "rule_confidence": top_candidate.get("rule_confidence"),
            "ml_probability": top_candidate.get("ml_probability"),
            "graph_distance": (
                top_candidate.get("decision_trace", {})
                .get("feature_snapshot", {})
                .get("graph_distance")
            ),
        }

    hypotheses = [
        {
            "change_id": row[0],
            "confidence": float(row[1]) if row[1] is not None else 0.0,
            "description": row[2],
            "created_at": row[3].isoformat() if row[3] else None,
        }
        for row in hypotheses_rows
    ]

    context = {
        "incident": {
            "title": incident[0],
            "severity": incident[1],
            "started_at": incident[2].isoformat(),
        },
        "affected_services": [{"id": s[0], "name": s[1]} for s in services],
        "hypotheses": hypotheses,
        "evidence": [{"type": e[0], "reference": e[1]} for e in evidence_rows],
        "candidates": candidates,
        "top_candidate": top_candidate,
        "context_flags": {
            "weak_signal": weak_signal,
            "close_competition": close_competition,
        },
    }

    explanation_result = generate_explanation(
        context, endpoint="rca", incident_id=incident_id
    )
    escalation = evaluate_escalation(context["context_flags"], rca_summary)
    quality = compute_rca_quality(
        candidates, context["context_flags"], escalation, rca_summary
    )

    return {
        "incident_id": incident_id,
        "explanation": explanation_result["explanation"],
        "explanation_source": explanation_result["source"],
        "confidence": hypotheses[0]["confidence"] if hypotheses else None,
        "rca_summary": rca_summary,
        "debug_trace": debug_trace,
        "predictions": candidates,
        "context_flags": context["context_flags"],
        "escalation": escalation,
        "quality": quality,
    }
