def get_downstream_services(conn, service_ids: set):
    """
    Recursively find services impacted downstream via dependencies.
    """
    cur = conn.cursor()

    visited = set(service_ids)
    frontier = set(service_ids)

    while frontier:
        cur.execute(
            """
            SELECT target_id
            FROM dependencies
            WHERE source_type = 'service'
              AND target_type = 'service'
              AND source_id = ANY(%s::uuid[])
            """,
            (list(frontier),),
        )

        next_level = {row[0] for row in cur.fetchall()}
        next_level -= visited

        visited.update(next_level)
        frontier = next_level

    cur.close()
    return visited