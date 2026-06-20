from __future__ import annotations

import base64

import yaml

from app.db import get_connection
from app.git.github_client import GitHubClient


def _decode_content(data: dict) -> str:
    raw = data.get("content", "")
    if data.get("encoding") == "base64":
        return base64.b64decode(raw).decode("utf-8", errors="replace")
    return raw


def clear_tenant_graph(tenant_id: str, keep_service_names: list[str] | None = None) -> dict:
    """Remove dependencies and orphan services so Git import replaces demo graph."""
    conn = get_connection(tenant_id=tenant_id)
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM dependencies d
        USING services s
        WHERE d.source_id = s.id AND s.tenant_id = %s
        """,
        (tenant_id,),
    )
    deps_removed = cur.rowcount

    if keep_service_names is not None:
        cur.execute(
            """
            DELETE FROM services
            WHERE tenant_id = %s
              AND name != ALL(%s)
              AND id NOT IN (
                  SELECT entity_id FROM incident_entities WHERE entity_type = 'service'
              )
            """,
            (tenant_id, keep_service_names or ["__none__"]),
        )
    else:
        cur.execute(
            """
            DELETE FROM services
            WHERE tenant_id = %s
              AND id NOT IN (
                  SELECT entity_id FROM incident_entities WHERE entity_type = 'service'
              )
            """,
            (tenant_id,),
        )
    services_removed = cur.rowcount

    conn.commit()
    cur.close()
    conn.close()
    return {"dependencies_removed": deps_removed, "services_removed": services_removed}


def ingest_services_from_github(
    client: GitHubClient,
    owner: str,
    repo: str,
    tenant_id: str,
    ref: str | None = None,
    *,
    replace_graph: bool = False,
) -> dict:
    """Discover service.yaml anywhere in the repo and upsert services + dependencies."""
    paths = client.list_service_yaml_paths(owner, repo, ref=ref)

    if not paths:
        return {
            "ingested": 0,
            "dependencies_added": 0,
            "paths_found": [],
            "error": (
                "No service.yaml files found. Add {service-name}/service.yaml to your repo, "
                "or use the SRCI sample_repo layout under backend/app/sample_repo/."
            ),
        }

    parsed: list[dict] = []
    for path in paths:
        try:
            files = client.get_contents(owner, repo, path, ref=ref)
            if isinstance(files, list):
                continue
            data = yaml.safe_load(_decode_content(files))
            if data and data.get("name"):
                parsed.append(data)
        except Exception:
            continue

    if not parsed:
        return {"ingested": 0, "dependencies_added": 0, "paths_found": paths, "error": "Could not parse service.yaml files"}

    imported_names = [d["name"] for d in parsed]

    if replace_graph:
        clear_tenant_graph(tenant_id, keep_service_names=imported_names)

    conn = get_connection(tenant_id=tenant_id)
    cur = conn.cursor()
    service_map: dict[str, str] = {}
    ingested = 0

    for data in parsed:
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

    deps_added = 0
    for data in parsed:
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

    return {
        "ingested": ingested,
        "dependencies_added": deps_added,
        "paths_found": paths,
        "service_names": imported_names,
    }


def list_known_services(tenant_id: str) -> list[str]:
    conn = get_connection(tenant_id=tenant_id)
    cur = conn.cursor()
    cur.execute("SELECT name FROM services WHERE tenant_id = %s ORDER BY name", (tenant_id,))
    names = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return names


def get_workspace_summary(tenant_id: str) -> dict:
    conn = get_connection(tenant_id=tenant_id)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM services WHERE tenant_id = %s", (tenant_id,))
    services = cur.fetchone()[0]
    cur.execute(
        """
        SELECT COUNT(*) FROM dependencies d
        JOIN services s ON d.source_id = s.id
        WHERE s.tenant_id = %s
        """,
        (tenant_id,),
    )
    deps = cur.fetchone()[0]
    cur.execute(
        """
        SELECT COUNT(*) FROM changes
        WHERE tenant_id = %s AND COALESCE(source, 'manual') LIKE 'github%%'
        """,
        (tenant_id,),
    )
    git_changes = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM incidents WHERE tenant_id = %s", (tenant_id,))
    incidents = cur.fetchone()[0]
    cur.execute(
        "SELECT COUNT(*) FROM git_connections WHERE tenant_id = %s", (tenant_id,)
    )
    connections = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {
        "services": services,
        "dependencies": deps,
        "git_changes": git_changes,
        "incidents": incidents,
        "git_connections": connections,
    }
