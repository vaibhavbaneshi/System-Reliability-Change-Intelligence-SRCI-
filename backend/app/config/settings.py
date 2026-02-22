import os

# Dependency types that propagate failures
PROPAGATING_DEPENDENCIES = set(
    os.getenv(
        "PROPAGATING_DEPENDENCIES",
        "runtime,sync_api,http,grpc"
    ).split(",")
)