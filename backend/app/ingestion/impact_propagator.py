import psycopg2
from collections import deque

def propagate_change_impact(db_url: str, change_id):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # 1) Get directly impacted services
    cur.execute(
        """
        SELECT entity_id
        FROM change_impacts
        WHERE change_id = %s
          AND entity_type = 'service'
          AND impact_level = 'high'
        """,
        (change_id,),
    )
    starting_services = [row[0] for row in cur.fetchall()]

    # 2) BFS through dependency graph
    queue = deque()
    visited = set()

    for service_id in starting_services:
        queue.append((service_id, 0))
        visited.add(service_id)

    while queue:
        current_service, depth = queue.popleft()

        # Find downstream services (who depends on me)
        cur.execute(
            """
            SELECT source_id
            FROM dependencies
            WHERE target_id = %s
              AND source_type = 'service'
              AND target_type = 'service'
            """,
            (current_service,),
        )

        for (downstream_service,) in cur.fetchall():
            if downstream_service in visited:
                continue

            visited.add(downstream_service)

            if depth == 0:
                impact = "medium"
            else:
                impact = "low"

            cur.execute(
                """
                INSERT INTO change_impacts (change_id, entity_type, entity_id, impact_level)
                VALUES (%s, 'service', %s, %s)
                """,
                (change_id, downstream_service, impact),
            )

            queue.append((downstream_service, depth + 1))

    conn.commit()
    cur.close()
    conn.close()