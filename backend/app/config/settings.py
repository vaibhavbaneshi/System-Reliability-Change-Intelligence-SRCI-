from __future__ import annotations

import os

# Dependency types that propagate failures
PROPAGATING_DEPENDENCIES = set(
    os.getenv(
        "PROPAGATING_DEPENDENCIES",
        "runtime,sync_api,http,grpc",
    ).split(",")
)

# Edge weights by dependency_type for impact propagation (Phase 15.4)
DEPENDENCY_TYPE_WEIGHTS: dict[str, float] = {
    "runtime": float(os.getenv("SRCI_WEIGHT_RUNTIME", "1.0")),
    "sync_api": float(os.getenv("SRCI_WEIGHT_SYNC_API", "0.9")),
    "http": float(os.getenv("SRCI_WEIGHT_HTTP", "0.75")),
    "grpc": float(os.getenv("SRCI_WEIGHT_GRPC", "0.8")),
    "async": float(os.getenv("SRCI_WEIGHT_ASYNC", "0.4")),
    "database": float(os.getenv("SRCI_WEIGHT_DATABASE", "0.85")),
    "cache": float(os.getenv("SRCI_WEIGHT_CACHE", "0.5")),
}

DEFAULT_DEPENDENCY_WEIGHT = float(os.getenv("SRCI_WEIGHT_DEFAULT", "0.5"))
DEPTH_DECAY = float(os.getenv("SRCI_GRAPH_DEPTH_DECAY", "0.85"))
MAX_GRAPH_DEPTH = int(os.getenv("SRCI_MAX_GRAPH_DEPTH", "10"))

CRITICALITY_MULTIPLIER = {
    "high": 1.0,
    "medium": 0.7,
    "low": 0.4,
}


def dependency_weight(dependency_type: str | None) -> float:
    if not dependency_type:
        return DEFAULT_DEPENDENCY_WEIGHT
    return DEPENDENCY_TYPE_WEIGHTS.get(dependency_type, DEFAULT_DEPENDENCY_WEIGHT)
