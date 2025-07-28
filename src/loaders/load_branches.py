import json
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def insert_branches(conn, branches):
    with conn.cursor() as cur:
        for branch in branches:
            cur.execute("""
                INSERT INTO branches (name, commit_id, commit_message, created_at, web_url)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (name, commit_id) DO NOTHING;
            """, (
                branch["name"],
                branch["commit_id"],
                branch["commit_message"],
                branch["created_at"],
                branch["web_url"]
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
    json_path = os.path.abspath(os.path.join(base_dir, "../../data/transformers/branches_transformed.json"))

    if not os.path.exists(json_path):
        print(f"[ERREUR] Fichier JSON introuvable : {json_path}")
        return

    branches = load_json(json_path)

    # Convertir les dates en objets datetime
    for b in branches:
        if b["created_at"]:
            b["created_at"] = datetime.fromisoformat(b["created_at"])

    try:
        with psycopg2.connect(**db_params) as conn:
            insert_branches(conn, branches)
            print("✅ Données des branches insérées avec succès dans la base de données.")
    except Exception as e:
        print(f"[❌] Erreur lors de l'insertion des branches : {e}")

if __name__ == "__main__":
    main()
