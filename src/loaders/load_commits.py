import os
import json
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def insert_commits(conn, commits):
    with conn.cursor() as cur:
        for commit in commits:
            cur.execute("""
                INSERT INTO commits (id, short_id, title, author_name, author_email, created_at, message, web_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
            """, (
                commit["id"],
                commit["short_id"],
                commit["title"],
                commit["author_name"],
                commit["author_email"],
                datetime.fromisoformat(commit["created_at"]) if commit["created_at"] else None,
                commit["message"],
                commit["web_url"]
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
    json_path = os.path.abspath(os.path.join(base_dir, "../../data/transformers/commits_transformed.json"))

    if not os.path.exists(json_path):
        print(f"[ERREUR] Fichier JSON introuvable : {json_path}")
        return

    commits = load_json(json_path)

    try:
        with psycopg2.connect(**db_params) as conn:
            insert_commits(conn, commits)
            print("✅ Données des commits insérées avec succès dans la base de données.")
    except Exception as e:
        print(f"[❌] Erreur lors de l'insertion des commits : {e}")

if __name__ == "__main__":
    main()
