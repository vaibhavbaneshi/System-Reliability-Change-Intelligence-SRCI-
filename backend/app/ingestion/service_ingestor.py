import os
import yaml
import psycopg2

REPO_PATH = "app/sample_repo"

def ingest_services(db_url: str):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    for service_dir in os.listdir(REPO_PATH):
        service_yaml = os.path.join(REPO_PATH, service_dir, "service.yaml")

        if not os.path.isfile(service_yaml):
            continue

        with open(service_yaml, "r") as f:
            data = yaml.safe_load(f)

        cur.execute(
            """
            INSERT INTO services (name, owner_team, criticality)
            VALUES (%s, %s, %s)
            ON CONFLICT (name) DO NOTHING
            """,
            (
                data["name"],
                data.get("owner_team"),
                data.get("criticality")
            )
        )

    conn.commit()
    cur.close()
    conn.close()