import os
import psycopg2
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression


MODEL_PATH = "app/ml/model.joblib"


def train_model(db_url: str):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    cur.execute("""
        SELECT impact_score,
               graph_distance,
               time_delta_hours,
               evidence_count,
               label
        FROM incident_change_features
    """)

    rows = cur.fetchall()
    conn.close()

    if not rows:
        raise ValueError("No training data found")

    X = []
    y = []

    for row in rows:
        impact, distance, time_delta, evidence, label = row
        X.append([impact, distance, time_delta, evidence])
        y.append(label)

    X = np.array(X)
    y = np.array(y)

    # 🔒 Guard against single-class training
    if len(set(y)) < 2:
        raise ValueError("Training data must contain at least 2 classes")

    model = LogisticRegression()
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)

    return {
        "samples": len(y),
        "model_path": MODEL_PATH
    }