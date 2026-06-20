from app.config.settings import PROPAGATING_DEPENDENCIES


def traverse_downstream_with_depth(
    conn,
    seed_ids,
    *,
    dependency_types=None,
    source_type="service",
    target_type="service",
):
    """
    BFS downstream traversal. Returns {service_id: depth} where depth 0 = seed.
    """
    if not seed_ids:
        return {}

    cur = conn.cursor()
    depths = {}
    frontier = []

    for sid in seed_ids:
        depths[sid] = 0
        frontier.append(sid)

    dep_clause = ""
    if dependency_types is not None:
        dep_clause = "AND dependency_type = ANY(%s)"

    while frontier:
        params = [frontier, source_type, target_type]
        if dependency_types is not None:
            params.append(list(dependency_types))

        cur.execute(
            f"""
            SELECT source_id
            FROM dependencies
            WHERE target_id = ANY(%s::uuid[])
              AND source_type = %s
              AND target_type = %s
              {dep_clause}
            """,
            params,
        )

        next_frontier = []
        current_depth = max(depths[s] for s in frontier)

        for (downstream_id,) in cur.fetchall():
            if downstream_id not in depths:
                depths[downstream_id] = current_depth + 1
                next_frontier.append(downstream_id)

        frontier = next_frontier

    cur.close()
    return depths


def traverse_downstream(
    conn,
    seed_ids,
    *,
    dependency_types=None,
    source_type="service",
    target_type="service",
):
    depths = traverse_downstream_with_depth(
        conn,
        seed_ids,
        dependency_types=dependency_types,
        source_type=source_type,
        target_type=target_type,
    )
    return set(depths.keys())


def get_downstream_services(conn, service_ids):
    return traverse_downstream(
        conn,
        service_ids,
        dependency_types=PROPAGATING_DEPENDENCIES,
    )
