import os
import json
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def insert_pipelines(conn, pipelines):
    with conn.cursor() as cur:
        for p in pipelines:
            cur.execute("""
                INSERT INTO pipelines (
                    id, status, ref, sha, created_at, updated_at, web_url, user_name, duration
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
            """, (
                p["id"],
                p["status"],
                p["ref"],
                p["sha"],
                datetime.fromisoformat(p["created_at"]) if p["created_at"] else None,
                datetime.fromisoformat(p["updated_at"]) if p["updated_at"] else None,
                p["web_url"],
                p["user"],
                p["duration"]
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
    json_path = os.path.abspath(os.path.join(base_dir, "../../data/transformers/pipelines_transformed.json"))

    if not os.path.exists(json_path):
        print(f"[ERREUR] Fichier JSON introuvable : {json_path}")
        return

    pipelines = load_json(json_path)

    try:
        with psycopg2.connect(**db_params) as conn:
            insert_pipelines(conn, pipelines)
            print("✅ Données des pipelines insérées avec succès dans la base de données.")
    except Exception as e:
        print(f"[❌] Erreur lors de l'insertion des pipelines : {e}")

if __name__ == "__main__":
    main()
