import psycopg2

from app.reasoning.graph_traversal import traverse_downstream_with_depth


def propagate_change_impact(db_url: str, change_id):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

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

    depths = traverse_downstream_with_depth(
        conn,
        starting_services,
        dependency_types=None,
    )

    for service_id, depth in depths.items():
        if depth == 0:
            continue

        impact = "medium" if depth == 1 else "low"
        cur.execute(
            """
            INSERT INTO change_impacts (change_id, entity_type, entity_id, impact_level)
            VALUES (%s, 'service', %s, %s)
            """,
            (change_id, service_id, impact),
        )

    conn.commit()
    cur.close()
    conn.close()
