from __future__ import annotations

import httpx


class GitHubError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(message)


class GitHubClient:
    BASE = "https://api.github.com"

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _request(self, method: str, path: str, **kwargs) -> dict | list:
        url = path if path.startswith("http") else f"{self.BASE}{path}"
        with httpx.Client(timeout=30.0) as client:
            resp = client.request(method, url, headers=self.headers, **kwargs)
        if resp.status_code >= 400:
            detail = resp.text[:300]
            raise GitHubError(resp.status_code, detail)
        if resp.status_code == 204:
            return {}
        return resp.json()

    def validate_repo(self, owner: str, repo: str) -> dict:
        return self._request("GET", f"/repos/{owner}/{repo}")

    def list_commits(self, owner: str, repo: str, branch: str, per_page: int = 20) -> list:
        return self._request(
            "GET",
            f"/repos/{owner}/{repo}/commits",
            params={"sha": branch, "per_page": per_page},
        )

    def get_commit(self, owner: str, repo: str, sha: str) -> dict:
        return self._request("GET", f"/repos/{owner}/{repo}/commits/{sha}")

    def list_open_pulls(self, owner: str, repo: str) -> list:
        return self._request(
            "GET",
            f"/repos/{owner}/{repo}/pulls",
            params={"state": "open", "per_page": 30},
        )

    def get_pull_files(self, owner: str, repo: str, pr_number: int) -> list:
        return self._request(
            "GET",
            f"/repos/{owner}/{repo}/pulls/{pr_number}/files",
            params={"per_page": 100},
        )

    def get_contents(self, owner: str, repo: str, path: str, ref: str | None = None) -> dict | list:
        params = {"ref": ref} if ref else {}
        return self._request("GET", f"/repos/{owner}/{repo}/contents/{path}", params=params)

    def list_root_contents(self, owner: str, repo: str, ref: str | None = None) -> list:
        result = self.get_contents(owner, repo, "", ref=ref)
        return result if isinstance(result, list) else [result]
