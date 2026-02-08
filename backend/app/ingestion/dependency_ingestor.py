import os
import yaml
import psycopg2

REPO_PATH = "app/sample_repo"

def ingest_dependencies(db_url: str):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # Build service name → id map
    cur.execute("SELECT id, name FROM services")
    service_map = {name: sid for sid, name in cur.fetchall()}

    for service_dir in os.listdir(REPO_PATH):
        service_yaml = os.path.join(REPO_PATH, service_dir, "service.yaml")

        if not os.path.isfile(service_yaml):
            continue

        with open(service_yaml, "r") as f:
            data = yaml.safe_load(f)

        source_id = service_map.get(data["name"])
        if not source_id:
            continue

        for dep_name in data.get("depends_on", []):
            target_id = service_map.get(dep_name)
            if not target_id:
                continue

            cur.execute(
                """
                INSERT INTO dependencies (source_type, source_id, target_type, target_id)
                VALUES ('service', %s, 'service', %s)
                """,
                (source_id, target_id)
            )

    conn.commit()
    cur.close()
    conn.close()