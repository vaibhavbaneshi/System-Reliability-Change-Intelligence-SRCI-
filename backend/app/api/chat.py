import os

import psycopg2
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.genai.explainer import generate_explanation
from app.reasoning.explanation_builder import build_explanation_response

router = APIRouter()
DATABASE_URL = os.getenv("DATABASE_URL", "")


class ChatRequest(BaseModel):
    message: str


SUGGESTED_QUESTIONS = [
    "Why is this incident likely caused by the top change?",
    "What evidence supports the leading hypothesis?",
    "How confident is the RCA and should we escalate?",
    "Which competing changes were considered?",
]


@router.get("/incidents/{incident_id}/chat/suggestions")
def chat_suggestions(incident_id: str):
    return {"incident_id": incident_id, "suggestions": SUGGESTED_QUESTIONS}


@router.post("/incidents/{incident_id}/chat")
def incident_chat(incident_id: str, body: ChatRequest):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT id FROM incidents WHERE id = %s", (incident_id,))
    if cur.fetchone() is None:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Incident not found")
    cur.close()
    conn.close()

    try:
        explanation_result = build_explanation_response(DATABASE_URL, incident_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    context = {
        "incident_id": incident_id,
        "user_question": body.message,
        "rca_summary": explanation_result.get("rca_summary"),
        "predictions": explanation_result.get("predictions", [])[:5],
        "context_flags": explanation_result.get("context_flags"),
        "escalation": explanation_result.get("escalation"),
        "quality": explanation_result.get("quality"),
        "evidence": explanation_result.get("debug_trace"),
    }

    llm_result = generate_explanation(
        {
            **context,
            "candidates": explanation_result.get("predictions", []),
            "affected_services": [],
            "hypotheses": [],
            "context_flags": explanation_result.get("context_flags", {}),
        },
        endpoint="chat",
        incident_id=incident_id,
    )

    top = (explanation_result.get("predictions") or [None])[0]
    citations = []
    if top:
        citations.append(
            {
                "type": "prediction",
                "change_id": top.get("change_id"),
                "hybrid_score": top.get("hybrid_score"),
                "confidence_band": top.get("confidence_band"),
            }
        )
        trace = top.get("decision_trace", {})
        if trace.get("components", {}).get("evidence_count", 0) > 0:
            citations.append({"type": "evidence", "count": trace["components"]["evidence_count"]})

    return {
        "incident_id": incident_id,
        "question": body.message,
        "answer": llm_result.get("explanation", ""),
        "source": llm_result.get("source", "template"),
        "citations": citations,
        "rca_summary": explanation_result.get("rca_summary"),
        "explanation_source": explanation_result.get("explanation_source"),
    }
