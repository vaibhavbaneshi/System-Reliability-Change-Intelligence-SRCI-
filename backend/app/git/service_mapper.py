from __future__ import annotations


def map_files_to_services(changed_files: list[str], known_services: list[str]) -> list[str]:
    """Match changed file paths to registered service names."""
    if not changed_files or not known_services:
        return []

    matched: set[str] = set()
    for path in changed_files:
        normalized = path.replace("\\", "/").lower()
        for service in known_services:
            svc = service.lower()
            if (
                normalized.startswith(f"{svc}/")
                or f"/{svc}/" in normalized
                or normalized.split("/")[0] == svc
            ):
                matched.add(service)

    return sorted(matched)


def infer_services_from_commit_message(message: str, known_services: list[str]) -> list[str]:
    """Fallback: service name mentioned in commit message."""
    if not message:
        return []
    lower = message.lower()
    return sorted(s for s in known_services if s.lower() in lower)
