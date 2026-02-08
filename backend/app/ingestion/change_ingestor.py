import psycopg2
from typing import List

def ingest_change(
    db_url: str,
    change_type: str,
    description: str,
    git_ref: str,
    services_touched: List[str],
):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # 1) Insert change record
    cur.execute(
        """
        INSERT INTO changes (change_type, description, git_ref)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (change_type, description, git_ref),
    )
    change_id = cur.fetchone()[0]

    # 2) Resolve service IDs for touched services
    cur.execute(
        """
        SELECT id, name
        FROM services
        WHERE name = ANY(%s)
        """,
        (services_touched,),
    )
    service_rows = cur.fetchall()

    # 3) Record direct impacts (highest confidence)
    for service_id, _ in service_rows:
        cur.execute(
            """
            INSERT INTO change_impacts (change_id, entity_type, entity_id, impact_level)
            VALUES (%s, 'service', %s, 'high')
            """,
            (change_id, service_id),
        )

    conn.commit()
    cur.close()
    conn.close()

    return change_id