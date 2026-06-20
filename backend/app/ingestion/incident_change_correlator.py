import psycopg2
from collections import defaultdict
from datetime import timedelta

from app.config.scoring_weights import (
    EVIDENCE_BOOST_MAX,
    EVIDENCE_BOOST_PER_ITEM,
    IMPACT_WEIGHTS,
    TEMPORAL_WINDOW_HOURS,
)
from app.ingestion.evidence_linker import format_change_evidence_reference
from app.reasoning.graph_traversal import get_downstream_services


def correlate_incident_to_changes(db_url: str, incident_id: str):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    cur.execute(
        "SELECT started_at FROM incidents WHERE id = %s",
        (incident_id,),
    )
    result = cur.fetchone()
    if result is None:
        raise ValueError(f"Incident with id {incident_id} not found")

    incident_started_at = result[0]

    cur.execute(
        """
        SELECT entity_id
        FROM incident_entities
        WHERE incident_id = %s
          AND entity_type = 'service'
        """,
        (incident_id,),
    )
    direct_services = {r[0] for r in cur.fetchall()}
    affected_services = get_downstream_services(conn, direct_services)

    window_start = incident_started_at - timedelta(hours=TEMPORAL_WINDOW_HOURS)
    cur.execute(
        """
        SELECT id
        FROM changes
        WHERE created_at BETWEEN %s AND %s
        """,
        (window_start, incident_started_at),
    )
    candidate_changes = [r[0] for r in cur.fetchall()]

    cur.execute(
        "DELETE FROM root_cause_hypotheses WHERE incident_id = %s",
        (incident_id,),
    )

    if not candidate_changes:
        conn.commit()
        cur.close()
        conn.close()
        return []

    cur.execute(
        """
        SELECT change_id, entity_id, impact_level
        FROM change_impacts
        WHERE change_id = ANY(%s::uuid[])
          AND entity_type = 'service'
        """,
        (candidate_changes,),
    )
    impacts_by_change = defaultdict(list)
    for change_id, entity_id, impact_level in cur.fetchall():
        impacts_by_change[change_id].append((entity_id, impact_level))

    cur.execute(
        """
        SELECT id, git_ref, created_at
        FROM changes
        WHERE id = ANY(%s::uuid[])
        """,
        (candidate_changes,),
    )
    change_meta = {row[0]: (row[1], row[2]) for row in cur.fetchall()}

    references = []
    ref_to_change = {}
    for change_id in candidate_changes:
        meta = change_meta.get(change_id)
        if meta:
            git_ref, created_at = meta
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

    hypotheses = []
    hypothesis_rows = []

    for change_id in candidate_changes:
        score = 0.0
        for service_id, impact_level in impacts_by_change.get(change_id, []):
            if service_id not in affected_services:
                continue
            score += IMPACT_WEIGHTS.get(impact_level, 0)

        if score > 0:
            evidence_count = evidence_counts.get(change_id, 0)
            score += min(EVIDENCE_BOOST_MAX, evidence_count * EVIDENCE_BOOST_PER_ITEM)
            score = min(score, 1.0)
            hypotheses.append((change_id, score))
            hypothesis_rows.append(
                (
                    incident_id,
                    change_id,
                    f"Change {change_id} is a likely contributor",
                    score,
                )
            )

    if hypothesis_rows:
        cur.executemany(
            """
            INSERT INTO root_cause_hypotheses
              (incident_id, change_id, description, confidence)
            VALUES (%s, %s, %s, %s)
            """,
            hypothesis_rows,
        )

    conn.commit()
    cur.close()
    conn.close()

    return hypotheses
