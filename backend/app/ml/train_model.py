import psycopg2
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)

MODEL_PATH = "app/ml/model.joblib"


def train_model(db_url: str):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # Load training data
    cur.execute("""
        SELECT temporal_proximity,
               service_overlap,
               graph_distance,
               criticality_score,
               label
        FROM incident_change_features
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if not rows:
        raise ValueError("No training data found")

    X = np.array([r[:-1] for r in rows], dtype=float)
    y = np.array([r[-1] for r in rows], dtype=int)

    # Ensure at least 2 classes exist
    if len(set(y)) < 2:
        raise ValueError("Training data must contain at least 2 classes")

    model = LogisticRegression()

    # Small dataset → train on full data (no split)
    if len(y) < 5:
        model.fit(X, y)

        # Save model
        joblib.dump(model, MODEL_PATH)

        return {
            "status": "trained_on_full_dataset",
            "samples": len(y),
            "note": "Dataset too small for train/test split"
        }

    # Normal dataset → split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model.fit(X_train, y_train)

    # Predictions
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    # Metrics
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_prob)
    cm = confusion_matrix(y_test, y_pred)

    # Save model
    joblib.dump(model, MODEL_PATH)

    return {
        "status": "trained_with_split",
        "samples": len(y),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "roc_auc": float(roc_auc),
        "confusion_matrix": cm.tolist()
    }