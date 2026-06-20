import psycopg2

from app.autonomy.config import LEARNING_LOOP_ENABLED, MIN_LABELS_FOR_RETRAIN
from app.ml.label_assigner import assign_labels_for_incident


def maybe_retrain(db_url: str) -> dict:
    if not LEARNING_LOOP_ENABLED:
        return {"retrained": False, "reason": "learning_loop_disabled"}

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT COUNT(DISTINCT incident_id), COUNT(*)
        FROM incident_change_features
        WHERE label IN (0, 1)
        """
    )
    incident_count, label_count = cur.fetchone()
    cur.execute(
        """
        SELECT COUNT(DISTINCT label)
        FROM incident_change_features
        WHERE label IN (0, 1)
        """
    )
    class_count = cur.fetchone()[0]
    cur.close()
    conn.close()

    if label_count < MIN_LABELS_FOR_RETRAIN or class_count < 2:
        return {
            "retrained": False,
            "reason": "insufficient_labeled_data",
            "label_count": label_count,
            "incident_count": incident_count,
        }

    try:
        from app.ml.train_model import train_model

        result = train_model(db_url)
        return {"retrained": True, "train_result": result}
    except Exception as exc:
        return {"retrained": False, "reason": str(exc)}


def apply_confirmed_feedback(db_url: str, incident_id: str, change_id: str) -> dict:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT change_id FROM incident_change_features
        WHERE incident_id = %s
        """,
        (incident_id,),
    )
    change_ids = [str(row[0]) for row in cur.fetchall()]
    cur.close()
    conn.close()

    labels = [{"change_id": cid, "label": 1 if cid == change_id else 0} for cid in change_ids]
    label_result = assign_labels_for_incident(db_url, incident_id, labels)
    retrain_result = maybe_retrain(db_url)
    return {"labels": label_result, "retrain": retrain_result}
