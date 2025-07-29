import os
import json
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

def load_events_to_postgres(json_path: str):
    load_dotenv()

    try:
        conn = psycopg2.connect(
            host=os.getenv("PGHOST"),
            port=os.getenv("PGPORT"),
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD"),
            dbname=os.getenv("PGDATABASE")
        )
        cur = conn.cursor()

        with open(json_path, "r", encoding="utf-8") as f:
            events = json.load(f)

        inserted_count = 0
        for event in events:
            try:
                cur.execute("""
                    INSERT INTO events (
                        id, action_name, target_type, author_username, 
                        created_at, target_title, target_id, 
                        project_id, author_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    event.get("id"),
                    event.get("action_name"),
                    event.get("target_type"),
                    event.get("author_username"),
                    event.get("created_at"),
                    event.get("target_title"),
                    event.get("target_id"),
                    event.get("project_id"),
                    event.get("author_id")
                ))
                inserted_count += 1
            except Exception as e:
                print(f"[⚠️] Événement ignoré (id={event.get('id')}): {e}")

        conn.commit()
        print(f"\n✅ {inserted_count} événements insérés avec succès dans la base de données.")
        cur.close()
        conn.close()

    except Exception as e:
        print(f"[❌] Erreur de connexion ou d'insertion : {e}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.abspath(os.path.join(base_dir, "../../data/transformers/events_transformed.json"))
    load_events_to_postgres(json_path)
