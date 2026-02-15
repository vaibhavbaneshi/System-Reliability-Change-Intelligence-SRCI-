import os
import psycopg2
import joblib
import numpy as np


MODEL_PATH = "app/ml/model.joblib"


def predict_for_incident(db_url: str, incident_id: str):
    if not os.path.exists(MODEL_PATH):
        raise RuntimeError("Model not trained yet")

    model = joblib.load(MODEL_PATH)

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # Get features
    cur.execute("""
        SELECT change_id,
               impact_score,
               graph_distance,
               time_delta_hours,
               evidence_count
        FROM incident_change_features
        WHERE incident_id = %s
    """, (incident_id,))

    rows = cur.fetchall()

    if not rows:
        raise ValueError("No features found for incident")

    # Clear previous hypotheses (ML version)
    cur.execute(
        "DELETE FROM root_cause_hypotheses WHERE incident_id = %s",
        (incident_id,),
    )

    for row in rows:
        change_id, impact, distance, time_delta, evidence = row

        X = np.array([[impact, distance, time_delta, evidence]])
        probability = model.predict_proba(X)[0][1]  # class 1 prob

        if probability > 0.1:  # threshold
            cur.execute("""
                INSERT INTO root_cause_hypotheses
                  (incident_id, change_id, description, confidence)
                VALUES (%s, %s, %s, %s)
            """, (
                incident_id,
                change_id,
                f"ML: Change {change_id} predicted contributor",
                float(probability)
            ))

    conn.commit()
    cur.close()
    conn.close()

    return {"status": "ml predictions stored"}