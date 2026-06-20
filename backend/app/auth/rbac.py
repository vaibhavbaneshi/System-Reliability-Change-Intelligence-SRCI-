from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


# Methods allowed per role (HTTP method + path prefix patterns)
ROLE_PERMISSIONS: dict[str, set[str]] = {
    Role.VIEWER: {
        "GET",
    },
    Role.ANALYST: {
        "GET",
        "POST:/incidents/",
        "POST:/changes/",
        "POST:/ingest",
        "POST:/feedback",
        "POST:/labels",
        "POST:/chat",
        "POST:/evaluate",
        "POST:/correlate",
        "POST:/features",
        "POST:/predict",
        "POST:/evidence",
        "POST:/run-rca",
    },
    Role.ADMIN: {"*"},
}


def role_allows(role: str, method: str, path: str) -> bool:
    perms = ROLE_PERMISSIONS.get(role, set())
    if "*" in perms:
        return True

    if method in perms and method == "GET":
        return True

    for perm in perms:
        if perm.startswith("POST:") and method == "POST":
            prefix = perm.split(":", 1)[1]
            if path.startswith(prefix):
                return True

    # Analyst can POST on most incident endpoints
    if role == Role.ANALYST and method == "POST":
        allowed_prefixes = (
            "/incidents/",
            "/changes/",
            "/ingest",
            "/feedback",
            "/labels",
        )
        return any(path.startswith(p) for p in allowed_prefixes)

    return False
