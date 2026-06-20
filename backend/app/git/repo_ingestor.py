from __future__ import annotations

import base64
import json

import yaml

from app.db import get_connection
from app.git.github_client import GitHubClient


def _decode_content(data: dict) -> str:
    raw = data.get("content", "")
    if data.get("encoding") == "base64":
        return base64.b64decode(raw).decode("utf-8", errors="replace")
    return raw


def ingest_services_from_github(
    client: GitHubClient,
    owner: str,
    repo: str,
    tenant_id: str,
    ref: str | None = None,
) -> dict:
    """Discover service.yaml files in repo root folders and upsert services + dependencies."""
    conn = get_connection(tenant_id=tenant_id)
    cur = conn.cursor()
    ingested = 0
    deps_added = 0

    try:
        entries = client.list_root_contents(owner, repo, ref=ref)
    except Exception as exc:
        cur.close()
        conn.close()
        return {"ingested": 0, "error": str(exc)}

    service_map: dict[str, str] = {}

    for entry in entries:
        if entry.get("type") != "dir":
            continue
        path = entry.get("path", "")
        try:
            files = client.get_contents(owner, repo, f"{path}/service.yaml", ref=ref)
            if isinstance(files, list):
                continue
            data = yaml.safe_load(_decode_content(files))
        except Exception:
            continue

        if not data or not data.get("name"):
            continue

        cur.execute(
            """
            INSERT INTO services (name, owner_team, criticality, tenant_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (tenant_id, name) DO UPDATE SET
                owner_team = EXCLUDED.owner_team,
                criticality = EXCLUDED.criticality
            RETURNING id
            """,
            (
                data["name"],
                data.get("owner_team"),
                data.get("criticality", "medium"),
                tenant_id,
            ),
        )
        service_id = str(cur.fetchone()[0])
        service_map[data["name"]] = service_id
        ingested += 1

    for entry in entries:
        if entry.get("type") != "dir":
            continue
        path = entry.get("path", "")
        try:
            files = client.get_contents(owner, repo, f"{path}/service.yaml", ref=ref)
            if isinstance(files, list):
                continue
            data = yaml.safe_load(_decode_content(files))
        except Exception:
            continue

        source_id = service_map.get(data.get("name"))
        if not source_id:
            continue

        for dep_name in data.get("depends_on", []):
            target_id = service_map.get(dep_name)
            if not target_id:
                cur.execute(
                    "SELECT id FROM services WHERE name = %s AND tenant_id = %s",
                    (dep_name, tenant_id),
                )
                row = cur.fetchone()
                if row:
                    target_id = str(row[0])
                else:
                    continue

            cur.execute(
                """
                INSERT INTO dependencies (source_type, source_id, target_type, target_id, dependency_type)
                SELECT 'service', %s::uuid, 'service', %s::uuid, 'runtime'
                WHERE NOT EXISTS (
                    SELECT 1 FROM dependencies
                    WHERE source_id = %s::uuid AND target_id = %s::uuid
                )
                """,
                (source_id, target_id, source_id, target_id),
            )
            deps_added += cur.rowcount

    conn.commit()
    cur.close()
    conn.close()
    return {"ingested": ingested, "dependencies_added": deps_added}


def list_known_services(tenant_id: str) -> list[str]:
    conn = get_connection(tenant_id=tenant_id)
    cur = conn.cursor()
    cur.execute("SELECT name FROM services WHERE tenant_id = %s ORDER BY name", (tenant_id,))
    names = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return names
