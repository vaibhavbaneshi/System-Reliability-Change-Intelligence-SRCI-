from __future__ import annotations

import json
from typing import Literal

from app.config.settings import (
    CRITICALITY_MULTIPLIER,
    DEPTH_DECAY,
    MAX_GRAPH_DEPTH,
    dependency_weight,
)
from app.db import get_connection

Direction = Literal["upstream", "downstream", "origin"]


def _impact_level(probability: float) -> str:
    if probability >= 0.75:
        return "high"
    if probability >= 0.45:
        return "medium"
    return "low"


def _risk_band(score: float) -> str:
    if score >= 0.7:
        return "high"
    if score >= 0.4:
        return "medium"
    return "low"


def _fetch_service_map(cur, service_ids: set) -> dict:
    if not service_ids:
        return {}
    cur.execute(
        """
        SELECT id, name, criticality
        FROM services
        WHERE id = ANY(%s::uuid[])
        """,
        (list(service_ids),),
    )
    return {
        str(r[0]): {"id": str(r[0]), "name": r[1], "criticality": r[2] or "medium"}
        for r in cur.fetchall()
    }


def _get_origin_service_ids(cur, change_id: str) -> list[str]:
    cur.execute(
        """
        SELECT entity_id
        FROM change_impacts
        WHERE change_id = %s AND entity_type = 'service'
        ORDER BY CASE impact_level WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END
        """,
        (change_id,),
    )
    rows = [str(r[0]) for r in cur.fetchall()]
    if rows:
        return rows

    cur.execute(
        """
        SELECT ci.entity_id
        FROM change_impacts ci
        WHERE ci.change_id = %s AND ci.entity_type = 'service'
        """,
        (change_id,),
    )
    return [str(r[0]) for r in cur.fetchall()]


def _sql_traverse(cur, function_name: str, seed_ids: list[str]) -> list[tuple]:
    if not seed_ids:
        return []
    cur.execute(
        f"""
        SELECT origin_id, service_id, depth, dependency_type
        FROM {function_name}(%s::uuid[], %s)
        """,
        (seed_ids, MAX_GRAPH_DEPTH),
    )
    return cur.fetchall()


def _build_nodes(
    rows: list[tuple],
    direction: Direction,
    service_map: dict,
    origins: set[str],
) -> list[dict]:
    nodes: dict[str, dict] = {}

    for origin_id, service_id, depth, dep_type in rows:
        sid = str(service_id)
        if sid in origins:
            continue

        edge_weight = dependency_weight(dep_type)
        propagation = edge_weight * (DEPTH_DECAY ** (depth - 1))
        svc = service_map.get(sid, {"id": sid, "name": sid, "criticality": "medium"})
        crit_mult = CRITICALITY_MULTIPLIER.get(svc.get("criticality", "medium"), 0.7)
        risk_contribution = round(propagation * crit_mult, 4)

        existing = nodes.get(sid)
        if existing and existing["propagation_probability"] >= propagation:
            continue

        nodes[sid] = {
            "service_id": sid,
            "service_name": svc["name"],
            "criticality": svc.get("criticality", "medium"),
            "depth": depth,
            "direction": direction,
            "dependency_type": dep_type,
            "edge_weight": round(edge_weight, 4),
            "propagation_probability": round(propagation, 4),
            "impact_level": _impact_level(propagation),
            "risk_contribution": risk_contribution,
            "origin_service_id": str(origin_id),
        }

    return sorted(nodes.values(), key=lambda n: (-n["propagation_probability"], n["depth"]))


def compute_failure_spread(upstream: list[dict], downstream: list[dict], origins: list[dict]) -> dict:
    all_nodes = upstream + downstream + origins
    if not all_nodes:
        return {
            "model": "probabilistic_decay",
            "expected_affected_count": 0.0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0,
        }

    probs = [n["propagation_probability"] for n in all_nodes]
    expected = round(sum(probs), 2)
    high = sum(1 for n in all_nodes if n["impact_level"] == "high")
    medium = sum(1 for n in all_nodes if n["impact_level"] == "medium")
    low = sum(1 for n in all_nodes if n["impact_level"] == "low")

    return {
        "model": "probabilistic_decay",
        "decay_factor": DEPTH_DECAY,
        "expected_affected_count": expected,
        "high_risk_count": high,
        "medium_risk_count": medium,
        "low_risk_count": low,
    }


def compute_risk_panel(
    upstream: list[dict],
    downstream: list[dict],
    origins: list[dict],
) -> dict:
    weighted = []
    factors = []

    for group, label in ((origins, "origin"), (downstream, "downstream"), (upstream, "upstream")):
        if not group:
            continue
        avg = sum(n["risk_contribution"] for n in group) / len(group)
        weighted.append(avg)
        factors.append(f"{label}_exposure: {avg:.3f} ({len(group)} services)")

    if origins:
        origin_crit = sum(
            CRITICALITY_MULTIPLIER.get(o.get("criticality", "medium"), 0.7) for o in origins
        ) / len(origins)
        weighted.append(origin_crit)
        factors.append(f"origin_criticality: {origin_crit:.3f}")

    score = round(sum(weighted) / len(weighted), 4) if weighted else 0.0
    band = _risk_band(score)

    return {
        "overall_risk_score": score,
        "risk_band": band,
        "factors": factors,
    }


def compute_blast_radius(change_id: str, *, persist: bool = True) -> dict:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM changes WHERE id = %s", (change_id,))
    if cur.fetchone() is None:
        cur.close()
        conn.close()
        raise ValueError(f"Change {change_id} not found")

    origin_ids = _get_origin_service_ids(cur, change_id)
    origin_set = set(origin_ids)

    downstream_rows = _sql_traverse(cur, "srci_graph_downstream", origin_ids)
    upstream_rows = _sql_traverse(cur, "srci_graph_upstream", origin_ids)

    all_ids = origin_set.copy()
    for _, sid, _, _ in downstream_rows + upstream_rows:
        all_ids.add(str(sid))

    service_map = _fetch_service_map(cur, all_ids)

    origins = [
        {
            "service_id": sid,
            "service_name": service_map.get(sid, {}).get("name", sid),
            "criticality": service_map.get(sid, {}).get("criticality", "medium"),
            "depth": 0,
            "direction": "origin",
            "dependency_type": None,
            "edge_weight": 1.0,
            "propagation_probability": 1.0,
            "impact_level": "high",
            "risk_contribution": CRITICALITY_MULTIPLIER.get(
                service_map.get(sid, {}).get("criticality", "medium"), 0.7
            ),
            "origin_service_id": sid,
        }
        for sid in origin_ids
    ]

    downstream = _build_nodes(downstream_rows, "downstream", service_map, origin_set)
    upstream = _build_nodes(upstream_rows, "upstream", service_map, origin_set)

    all_affected = origins + downstream + upstream
    max_depth = max((n["depth"] for n in all_affected), default=0)
    total = len(all_affected)

    blast_score = round(
        min(1.0, sum(n["propagation_probability"] for n in all_affected) / max(total, 1)),
        4,
    )

    failure_spread = compute_failure_spread(upstream, downstream, origins)
    risk_panel = compute_risk_panel(upstream, downstream, origins)

    result = {
        "change_id": change_id,
        "origin_services": [
            {"id": o["service_id"], "name": o["service_name"], "criticality": o["criticality"]}
            for o in origins
        ],
        "blast_radius": {
            "total_services": total,
            "downstream_count": len(downstream),
            "upstream_count": len(upstream),
            "score": blast_score,
            "max_depth": max_depth,
        },
        "downstream": downstream,
        "upstream": upstream,
        "failure_spread": failure_spread,
        "risk_panel": risk_panel,
    }

    if persist:
        cur.execute(
            """
            INSERT INTO change_blast_radius
                (change_id, blast_score, total_services, max_depth,
                 upstream_count, downstream_count, risk_score, risk_band, analysis)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (change_id) DO UPDATE SET
                blast_score = EXCLUDED.blast_score,
                total_services = EXCLUDED.total_services,
                max_depth = EXCLUDED.max_depth,
                upstream_count = EXCLUDED.upstream_count,
                downstream_count = EXCLUDED.downstream_count,
                risk_score = EXCLUDED.risk_score,
                risk_band = EXCLUDED.risk_band,
                analysis = EXCLUDED.analysis,
                computed_at = NOW()
            """,
            (
                change_id,
                blast_score,
                total,
                max_depth,
                len(upstream),
                len(downstream),
                risk_panel["overall_risk_score"],
                risk_panel["risk_band"],
                json.dumps(result),
            ),
        )
        conn.commit()

    cur.close()
    conn.close()
    return result


def get_cached_blast_radius(change_id: str) -> dict | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT analysis FROM change_blast_radius WHERE change_id = %s",
        (change_id,),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row and row[0]:
        return row[0] if isinstance(row[0], dict) else json.loads(row[0])
    return None


def compute_service_failure_risk(service_id: str) -> dict:
    """Hypothetical blast radius if this service fails."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, criticality FROM services WHERE id = %s", (service_id,))
    row = cur.fetchone()
    if row is None:
        cur.close()
        conn.close()
        raise ValueError(f"Service {service_id} not found")

    origin_ids = [str(row[0])]
    downstream_rows = _sql_traverse(cur, "srci_graph_downstream", origin_ids)
    upstream_rows = _sql_traverse(cur, "srci_graph_upstream", origin_ids)

    all_ids = set(origin_ids)
    for _, sid, _, _ in downstream_rows + upstream_rows:
        all_ids.add(str(sid))
    service_map = _fetch_service_map(cur, all_ids)
    origin_set = set(origin_ids)

    origins = [
        {
            "service_id": str(row[0]),
            "service_name": row[1],
            "criticality": row[2] or "medium",
            "depth": 0,
            "direction": "origin",
            "dependency_type": None,
            "edge_weight": 1.0,
            "propagation_probability": 1.0,
            "impact_level": "high",
            "risk_contribution": CRITICALITY_MULTIPLIER.get(row[2] or "medium", 0.7),
            "origin_service_id": str(row[0]),
        }
    ]

    downstream = _build_nodes(downstream_rows, "downstream", service_map, origin_set)
    upstream = _build_nodes(upstream_rows, "upstream", service_map, origin_set)
    failure_spread = compute_failure_spread(upstream, downstream, origins)
    risk_panel = compute_risk_panel(upstream, downstream, origins)

    cur.close()
    conn.close()

    return {
        "service_id": str(row[0]),
        "service_name": row[1],
        "criticality": row[2],
        "downstream": downstream,
        "upstream": upstream,
        "failure_spread": failure_spread,
        "risk_panel": risk_panel,
        "blast_radius_pct": round(risk_panel["overall_risk_score"] * 100, 1),
    }
