from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timezone

from app.db import get_bypass_connection, get_connection
from app.graph.blast_radius import compute_blast_radius
from app.git.github_client import GitHubClient, GitHubError
from app.git.repo_ingestor import ingest_services_from_github, list_known_services
from app.git.service_mapper import infer_services_from_commit_message, map_files_to_services
from app.ingestion.change_ingestor import ingest_change

DATABASE_URL = os.getenv("DATABASE_URL", "")
WEBHOOK_BASE = os.getenv("SRCI_WEBHOOK_BASE_URL", "http://127.0.0.1:8001")


def _merge_recommendation(risk_band: str | None) -> str:
    if risk_band == "high":
        return "review_required"
    if risk_band == "medium":
        return "caution"
    return "approve"


def _risk_from_blast(blast: dict | None) -> tuple[str | None, float | None]:
    if not blast:
        return None, None
    panel = blast.get("risk_panel") or {}
    return panel.get("risk_band"), panel.get("overall_risk_score")


def _event_exists(cur, connection_id: str, git_ref: str) -> bool:
    cur.execute(
        """
        SELECT 1 FROM git_events
        WHERE connection_id = %s AND git_ref = %s
        LIMIT 1
        """,
        (connection_id, git_ref),
    )
    return cur.fetchone() is not None


def _record_git_event(
    cur,
    connection_id: str,
    event_type: str,
    git_ref: str | None,
    *,
    pr_number: int | None = None,
    commit_message: str | None = None,
    author: str | None = None,
    services_touched: list[str] | None = None,
    change_id: str | None = None,
    payload: dict | None = None,
) -> None:
    cur.execute(
        """
        INSERT INTO git_events
            (connection_id, event_type, git_ref, pr_number, commit_message, author,
             services_touched, change_id, payload)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
        ON CONFLICT DO NOTHING
        """,
        (
            connection_id,
            event_type,
            git_ref,
            pr_number,
            commit_message,
            author,
            services_touched or [],
            change_id,
            json.dumps(payload or {}),
        ),
    )


def _ingest_git_change(
    tenant_id: str,
    connection_id: str,
    description: str,
    git_ref: str,
    services: list[str],
    source: str,
    pr_number: int | None = None,
) -> str | None:
    if not services:
        return None

    change_id = ingest_change(
        DATABASE_URL,
        "code",
        description,
        git_ref,
        services,
        tenant_id=tenant_id,
    )

    conn = get_connection(tenant_id=tenant_id)
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE changes
        SET source = %s, commit_sha = %s, pr_number = %s, git_connection_id = %s
        WHERE id = %s
        """,
        (source, git_ref, pr_number, connection_id, change_id),
    )
    conn.commit()
    cur.close()
    conn.close()

    try:
        compute_blast_radius(str(change_id), persist=True)
    except Exception:
        pass

    return str(change_id)


def process_commit(
    connection: dict,
    sha: str,
    message: str,
    author: str,
    files: list[str],
    *,
    source: str = "github_push",
    pr_number: int | None = None,
) -> dict:
    conn = get_connection(tenant_id=connection["tenant_id"])
    cur = conn.cursor()

    if _event_exists(cur, connection["id"], sha):
        cur.close()
        conn.close()
        return {"skipped": True, "reason": "already_processed", "git_ref": sha}

    known = list_known_services(connection["tenant_id"])
    services = map_files_to_services(files, known)
    if not services:
        services = infer_services_from_commit_message(message, known)
    if not services and known:
        services = [known[0]]

    change_id = None
    if services:
        change_id = _ingest_git_change(
            connection["tenant_id"],
            connection["id"],
            message or f"Commit {sha[:8]}",
            sha,
            services,
            source,
            pr_number=pr_number,
        )

    _record_git_event(
        cur,
        connection["id"],
        "push" if not pr_number else "pull_request",
        sha,
        pr_number=pr_number,
        commit_message=message,
        author=author,
        services_touched=services,
        change_id=change_id,
    )
    conn.commit()
    cur.close()
    conn.close()

    return {
        "git_ref": sha,
        "services_touched": services,
        "change_id": change_id,
        "skipped": False,
    }


def check_pull_request(connection: dict, pr: dict) -> dict:
    client = GitHubClient(connection["access_token"])
    files_data = client.get_pull_files(connection["owner"], connection["repo"], pr["number"])
    files = [f.get("filename", "") for f in files_data]

    known = list_known_services(connection["tenant_id"])
    services = map_files_to_services(files, known)
    if not services:
        services = infer_services_from_commit_message(pr.get("title", ""), known)

    head_sha = pr.get("head", {}).get("sha", "")
    title = pr.get("title", "PR")
    result = process_commit(
        connection,
        head_sha,
        f"PR #{pr['number']}: {title}",
        pr.get("user", {}).get("login", "unknown"),
        files,
        source="github_pr",
        pr_number=pr["number"],
    )

    blast = None
    if result.get("change_id"):
        try:
            blast = compute_blast_radius(result["change_id"], persist=True)
        except Exception:
            pass

    risk_band, risk_score = _risk_from_blast(blast)
    recommendation = _merge_recommendation(risk_band)

    conn = get_connection(tenant_id=connection["tenant_id"])
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO pull_request_checks
            (connection_id, tenant_id, pr_number, title, head_sha, base_branch, state,
             risk_band, risk_score, blast_radius, merge_recommendation, services_touched,
             change_id, html_url, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, NOW())
        ON CONFLICT (connection_id, pr_number) DO UPDATE SET
            title = EXCLUDED.title,
            head_sha = EXCLUDED.head_sha,
            state = EXCLUDED.state,
            risk_band = EXCLUDED.risk_band,
            risk_score = EXCLUDED.risk_score,
            blast_radius = EXCLUDED.blast_radius,
            merge_recommendation = EXCLUDED.merge_recommendation,
            services_touched = EXCLUDED.services_touched,
            change_id = EXCLUDED.change_id,
            html_url = EXCLUDED.html_url,
            updated_at = NOW()
        """,
        (
            connection["id"],
            connection["tenant_id"],
            pr["number"],
            title,
            head_sha,
            pr.get("base", {}).get("ref", "main"),
            pr.get("state", "open"),
            risk_band,
            risk_score,
            json.dumps(blast or {}),
            recommendation,
            services,
            result.get("change_id"),
            pr.get("html_url"),
        ),
    )
    conn.commit()
    cur.close()
    conn.close()

    return {
        "pr_number": pr["number"],
        "title": title,
        "services_touched": services,
        "change_id": result.get("change_id"),
        "risk_band": risk_band,
        "risk_score": risk_score,
        "merge_recommendation": recommendation,
        "blast_radius": blast.get("blast_radius") if blast else None,
        "html_url": pr.get("html_url"),
    }


def sync_connection(connection_id: str, tenant_id: str) -> dict:
    conn = get_bypass_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, tenant_id, owner, repo, default_branch, access_token,
               ingest_services_from_repo
        FROM git_connections
        WHERE id = %s AND tenant_id = %s
        """,
        (connection_id, tenant_id),
    )
    row = cur.fetchone()
    if row is None:
        cur.close()
        conn.close()
        raise ValueError("Git connection not found")

    connection = {
        "id": str(row[0]),
        "tenant_id": str(row[1]),
        "owner": row[2],
        "repo": row[3],
        "default_branch": row[4],
        "access_token": row[5],
        "ingest_services_from_repo": row[6],
    }

    client = GitHubClient(connection["access_token"])
    summary = {"commits": [], "pull_requests": [], "services_ingested": None}

    try:
        if connection["ingest_services_from_repo"]:
            summary["services_ingested"] = ingest_services_from_github(
                client,
                connection["owner"],
                connection["repo"],
                connection["tenant_id"],
                ref=connection["default_branch"],
                replace_graph=True,
            )

        commits = client.list_commits(
            connection["owner"],
            connection["repo"],
            connection["default_branch"],
            per_page=15,
        )
        for commit in commits:
            sha = commit.get("sha")
            detail = client.get_commit(connection["owner"], connection["repo"], sha)
            files = [f.get("filename", "") for f in detail.get("files", [])]
            msg = commit.get("commit", {}).get("message", "")
            author = commit.get("commit", {}).get("author", {}).get("name", "unknown")
            result = process_commit(connection, sha, msg, author, files)
            if not result.get("skipped"):
                summary["commits"].append(result)

        pulls = client.list_open_pulls(connection["owner"], connection["repo"])
        for pr in pulls:
            check = check_pull_request(connection, pr)
            summary["pull_requests"].append(check)

        status = "success"
        message = f"Synced {len(summary['commits'])} commits, {len(summary['pull_requests'])} PRs"
    except GitHubError as exc:
        status = "error"
        message = str(exc)
    except Exception as exc:
        status = "error"
        message = str(exc)

    cur.execute(
        """
        UPDATE git_connections
        SET last_sync_at = NOW(), last_sync_status = %s, last_sync_message = %s
        WHERE id = %s
        """,
        (status, message, connection_id),
    )
    conn.commit()
    cur.close()
    conn.close()

    return {"status": status, "message": message, **summary}


def verify_github_signature(payload: bytes, signature: str | None, secret: str) -> bool:
    if not signature or not secret:
        return False
    expected = "sha256=" + hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def handle_github_webhook(payload: dict, headers: dict) -> dict:
    event = headers.get("x-github-event", headers.get("X-GitHub-Event", ""))
    repo = payload.get("repository", {})
    full_name = repo.get("full_name", "")
    if not full_name or "/" not in full_name:
        return {"processed": False, "reason": "no repository"}

    owner, repo_name = full_name.split("/", 1)
    conn = get_bypass_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, tenant_id, owner, repo, default_branch, access_token, webhook_secret
        FROM git_connections
        WHERE owner = %s AND repo = %s AND auto_sync = TRUE
        LIMIT 1
        """,
        (owner, repo_name),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row is None:
        return {"processed": False, "reason": "no matching connection"}

    connection = {
        "id": str(row[0]),
        "tenant_id": str(row[1]),
        "owner": row[2],
        "repo": row[3],
        "default_branch": row[4],
        "access_token": row[5],
        "webhook_secret": row[6],
    }

    if event == "push":
        results = []
        for commit in payload.get("commits", []):
            sha = commit.get("id")
            files = commit.get("modified", []) + commit.get("added", []) + commit.get("removed", [])
            results.append(
                process_commit(
                    connection,
                    sha,
                    commit.get("message", ""),
                    commit.get("author", {}).get("name", "unknown"),
                    files,
                )
            )
        return {"processed": True, "event": "push", "results": results}

    if event == "pull_request":
        action = payload.get("action")
        pr = payload.get("pull_request", {})
        if action in ("opened", "synchronize", "reopened"):
            check = check_pull_request(connection, pr)
            return {"processed": True, "event": "pull_request", "check": check}
        return {"processed": True, "event": "pull_request", "action": action, "skipped": True}

    return {"processed": False, "reason": f"unsupported event {event}"}


def generate_webhook_secret() -> str:
    return secrets.token_urlsafe(32)


def webhook_url_for_connection(connection_id: str) -> str:
    return f"{WEBHOOK_BASE.rstrip('/')}/webhooks/github"
