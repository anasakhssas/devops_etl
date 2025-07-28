import os
import json
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def insert_projects(conn, projects):
    with conn.cursor() as cur:
        for p in projects:
            cur.execute("""
                INSERT INTO projects (
                    id, name, description, created_at, web_url,
                    namespace, visibility, default_branch
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
            """, (
                p["id"],
                p["name"],
                p.get("description"),
                datetime.fromisoformat(p["created_at"]) if p.get("created_at") else None,
                p["web_url"],
                p.get("namespace"),
                p.get("visibility"),
                p.get("default_branch")
            ))
        conn.commit()

def main():
    load_dotenv()

    db_params = {
        "host": os.getenv("PGHOST"),
        "port": os.getenv("PGPORT"),
        "user": os.getenv("PGUSER"),
        "password": os.getenv("PGPASSWORD"),
        "dbname": os.getenv("PGDATABASE")
    }

    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.abspath(os.path.join(base_dir, "../../data/transformers/projects_transformed.json"))

    if not os.path.exists(json_path):
        print(f"[ERREUR] Fichier JSON introuvable : {json_path}")
        return

    projects = load_json(json_path)

    try:
        with psycopg2.connect(**db_params) as conn:
            insert_projects(conn, projects)
            print("✅ Données des projets insérées avec succès dans la base de données.")
    except Exception as e:
        print(f"[❌] Erreur lors de l'insertion des projets : {e}")

if __name__ == "__main__":
    main()
