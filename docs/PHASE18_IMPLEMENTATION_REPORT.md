# Phase 18 — Git Plug-and-Play

**Date:** 2026-06-20

## End-user flow

1. Open **Integrations** (`/integrations`)
2. Enter GitHub owner, repo, and Personal Access Token (`repo` scope)
3. Click **Connect & sync** — SRCI imports `service.yaml` files, recent commits, and open PRs
4. Copy webhook URL + secret into GitHub repo settings (optional, for live updates)
5. View **Changes** and **Pull Requests** in the UI — no terminal required
6. When incidents occur, investigate under **Incidents** as before

## APIs

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/git/connect` | Connect repo + initial sync |
| GET | `/git/connections` | List connections |
| POST | `/git/connections/{id}/sync` | Manual sync |
| GET | `/git/pull-requests` | PR pre-merge checks |
| GET | `/git/events` | Recent Git activity |
| POST | `/webhooks/github` | GitHub push / pull_request webhook |

## Env

| Variable | Default | Purpose |
|----------|---------|---------|
| `SRCI_WEBHOOK_BASE_URL` | `http://127.0.0.1:8001` | Webhook URL shown in UI |

## Service mapping

Changed files are matched to services by path (`auth-service/...`).  
Repo layout: `{service-name}/service.yaml` with optional `depends_on`.

## Limitations (v1)

- GitHub only (not GitLab/Bitbucket yet)
- PAT auth (not GitHub App OAuth UI)
- Webhook requires manual paste in GitHub settings
- Incidents still via API/autonomy — not from Git directly
