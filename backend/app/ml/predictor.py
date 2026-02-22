import psycopg2
import numpy as np
import joblib

MODEL_PATH = "app/ml/model.joblib"


def predict_for_incident(db_url: str, incident_id: str):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # Load model
    model = joblib.load(MODEL_PATH)

    # Fetch features for this incident
    cur.execute("""
        SELECT change_id,
               temporal_proximity,
               service_overlap,
               graph_distance,
               criticality_score
        FROM incident_change_features
        WHERE incident_id = %s
    """, (incident_id,))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    if not rows:
        return {
            "incident_id": incident_id,
            "predictions": [],
            "note": "No features found for this incident"
        }

    predictions = []

    for row in rows:
        change_id = row[0]
        features = np.array(row[1:]).reshape(1, -1)

        probability = model.predict_proba(features)[0][1]

        predictions.append({
            "change_id": change_id,
            "ml_probability": float(probability)
        })

    # Sort highest probability first
    predictions.sort(key=lambda x: x["ml_probability"], reverse=True)

    return {
        "incident_id": incident_id,
        "predictions": predictions
    }