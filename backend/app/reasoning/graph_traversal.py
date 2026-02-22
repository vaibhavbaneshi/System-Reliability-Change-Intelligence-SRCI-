from app.config.settings import PROPAGATING_DEPENDENCIES

def get_downstream_services(conn, service_ids):
    if not service_ids:
        return set()

    cur = conn.cursor()

    visited = set(service_ids)
    frontier = set(service_ids)

    while frontier:
        cur.execute(
            """
            SELECT source_id
            FROM dependencies
            WHERE target_id = ANY(%s::uuid[])
              AND dependency_type = ANY(%s)
            """,
            (
                list(frontier),
                list(PROPAGATING_DEPENDENCIES),
            ),
        )

        next_level = {row[0] for row in cur.fetchall()} - visited

        visited.update(next_level)
        frontier = next_level

    cur.close()
    return visited