from __future__ import annotations

import secrets
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app.auth.config import AuthContext
from app.auth.deps import require_admin, require_auth, require_role
from app.db import get_bypass_connection, get_connection
from app.git.github_client import GitHubClient, GitHubError
from app.git.repo_ingestor import get_workspace_summary, ingest_services_from_github
from app.git.sync import (
    generate_webhook_secret,
    handle_github_webhook,
    sync_connection,
    verify_github_signature,
    webhook_url_for_connection,
)

router = APIRouter(tags=["git"])


class GitConnectRequest(BaseModel):
    owner: str = Field(..., min_length=1)
    repo: str = Field(..., min_length=1)
    access_token: str = Field(..., min_length=10)
    default_branch: str = "main"
    ingest_services_from_repo: bool = True


def _mask_token(token: str) -> str:
    if len(token) <= 8:
        return "****"
    return f"{token[:4]}...{token[-4:]}"


def _serialize_connection(row) -> dict:
    return {
        "id": str(row[0]),
        "provider": row[1],
        "owner": row[2],
        "repo": row[3],
        "full_name": f"{row[2]}/{row[3]}",
        "default_branch": row[4],
        "token_masked": _mask_token(row[5]),
        "auto_sync": row[6],
        "ingest_services_from_repo": row[7],
        "last_sync_at": row[8].isoformat() if row[8] else None,
        "last_sync_status": row[9],
        "last_sync_message": row[10],
        "created_at": row[11].isoformat(),
        "webhook_url": webhook_url_for_connection(str(row[0])),
    }


@router.post("/git/connect")
def connect_git(
    req: GitConnectRequest,
    auth: AuthContext = Depends(require_role("admin", "analyst")),
):
    client = GitHubClient(req.access_token)
    try:
        repo_meta = client.validate_repo(req.owner, req.repo)
    except GitHubError as exc:
        raise HTTPException(status_code=400, detail=f"GitHub validation failed: {exc}") from exc

    branch = req.default_branch or repo_meta.get("default_branch", "main")
    webhook_secret = generate_webhook_secret()

    conn = get_connection(tenant_id=auth.tenant_id)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO git_connections
            (tenant_id, owner, repo, default_branch, access_token, webhook_secret,
             ingest_services_from_repo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (tenant_id, owner, repo) DO UPDATE SET
            default_branch = EXCLUDED.default_branch,
            access_token = EXCLUDED.access_token,
            webhook_secret = EXCLUDED.webhook_secret,
            ingest_services_from_repo = EXCLUDED.ingest_services_from_repo
        RETURNING id, provider, owner, repo, default_branch, access_token,
                  auto_sync, ingest_services_from_repo, last_sync_at,
                  last_sync_status, last_sync_message, created_at
        """,
        (
            auth.tenant_id,
            req.owner,
            req.repo,
            branch,
            req.access_token,
            webhook_secret,
            req.ingest_services_from_repo,
        ),
    )
    row = cur.fetchone()
    connection_id = str(row[0])
    conn.commit()
    cur.close()
    conn.close()

    services_result = None
    if req.ingest_services_from_repo:
        services_result = ingest_services_from_github(
            client,
            req.owner,
            req.repo,
            auth.tenant_id,
            ref=branch,
            replace_graph=True,
        )

    sync_result = sync_connection(connection_id, auth.tenant_id)

    return {
        "connection": _serialize_connection(row),
        "webhook_secret": webhook_secret,
        "webhook_setup": {
            "url": webhook_url_for_connection(connection_id),
            "secret": webhook_secret,
            "events": ["push", "pull_request"],
            "instructions": (
                "In GitHub: Settings → Webhooks → Add webhook. "
                "Paste URL and secret. Select 'push' and 'pull request' events."
            ),
        },
        "services_ingested": services_result,
        "initial_sync": sync_result,
    }


@router.get("/git/workspace")
def git_workspace(auth: AuthContext = Depends(require_auth)):
    """Summary of services, dependencies, and Git-sourced changes for the tenant."""
    return get_workspace_summary(auth.tenant_id)


@router.get("/git/connections")
def list_connections(auth: AuthContext = Depends(require_auth)):
    conn = get_connection(tenant_id=auth.tenant_id)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, provider, owner, repo, default_branch, access_token,
               auto_sync, ingest_services_from_repo, last_sync_at,
               last_sync_status, last_sync_message, created_at
        FROM git_connections
        WHERE tenant_id = %s
        ORDER BY created_at DESC
        """,
        (auth.tenant_id,),
    )
    rows = [_serialize_connection(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return {"connections": rows}


@router.delete("/git/connections/{connection_id}")
def disconnect_git(connection_id: str, auth: AuthContext = Depends(require_admin)):
    conn = get_connection(tenant_id=auth.tenant_id)
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM git_connections WHERE id = %s AND tenant_id = %s RETURNING id",
        (connection_id, auth.tenant_id),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Connection not found")
    return {"deleted": True}


@router.post("/git/connections/{connection_id}/sync")
def sync_git(connection_id: str, auth: AuthContext = Depends(require_auth)):
    try:
        return sync_connection(connection_id, auth.tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/git/pull-requests")
def list_pull_requests(auth: AuthContext = Depends(require_auth)):
    conn = get_connection(tenant_id=auth.tenant_id)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT pr.id, pr.connection_id, pr.pr_number, pr.title, pr.head_sha,
               pr.base_branch, pr.state, pr.risk_band, pr.risk_score,
               pr.merge_recommendation, pr.services_touched, pr.change_id,
               pr.html_url, pr.updated_at, gc.owner, gc.repo
        FROM pull_request_checks pr
        JOIN git_connections gc ON gc.id = pr.connection_id
        WHERE pr.tenant_id = %s
        ORDER BY pr.updated_at DESC
        LIMIT 50
        """,
        (auth.tenant_id,),
    )
    rows = [
        {
            "id": str(r[0]),
            "connection_id": str(r[1]),
            "pr_number": r[2],
            "title": r[3],
            "head_sha": r[4],
            "base_branch": r[5],
            "state": r[6],
            "risk_band": r[7],
            "risk_score": float(r[8]) if r[8] is not None else None,
            "merge_recommendation": r[9],
            "services_touched": r[10] or [],
            "change_id": str(r[11]) if r[11] else None,
            "html_url": r[12],
            "updated_at": r[13].isoformat(),
            "repo": f"{r[14]}/{r[15]}",
        }
        for r in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return {"pull_requests": rows}


@router.get("/git/events")
def list_git_events(limit: int = 30, auth: AuthContext = Depends(require_auth)):
    conn = get_connection(tenant_id=auth.tenant_id)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT ge.id, ge.event_type, ge.git_ref, ge.pr_number, ge.commit_message,
               ge.author, ge.services_touched, ge.change_id, ge.created_at,
               gc.owner, gc.repo
        FROM git_events ge
        JOIN git_connections gc ON gc.id = ge.connection_id
        WHERE gc.tenant_id = %s
        ORDER BY ge.created_at DESC
        LIMIT %s
        """,
        (auth.tenant_id, limit),
    )
    rows = [
        {
            "id": str(r[0]),
            "event_type": r[1],
            "git_ref": r[2],
            "pr_number": r[3],
            "commit_message": r[4],
            "author": r[5],
            "services_touched": r[6] or [],
            "change_id": str(r[7]) if r[7] else None,
            "created_at": r[8].isoformat(),
            "repo": f"{r[9]}/{r[10]}",
        }
        for r in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return {"events": rows}


webhook_router = APIRouter(tags=["webhooks"])


@webhook_router.post("/webhooks/github")
async def github_webhook(request: Request):
    body = await request.body()
    try:
        payload = __import__("json").loads(body)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON") from exc

    full_name = payload.get("repository", {}).get("full_name", "")
    if full_name and "/" in full_name:
        owner, repo_name = full_name.split("/", 1)
        conn = get_bypass_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT webhook_secret FROM git_connections WHERE owner = %s AND repo = %s LIMIT 1",
            (owner, repo_name),
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row and row[0]:
            sig = request.headers.get("x-hub-signature-256")
            if not verify_github_signature(body, sig, row[0]):
                raise HTTPException(status_code=401, detail="Invalid webhook signature")

    headers = {k: v for k, v in request.headers.items()}
    return handle_github_webhook(payload, headers)
