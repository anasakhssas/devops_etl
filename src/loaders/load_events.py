import os
import json
from datetime import datetime
from src.loaders.database.db_connection import get_db_connection  # adapte le chemin si besoin

def load_events(json_path="data/transformers/events_transformed.json"):
    """Charge et insère les événements depuis un fichier JSON vers la base de données."""

    if not os.path.exists(json_path):
        print(f"[❌] Fichier introuvable : {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        events = json.load(f)

    if not events:
        print("[ℹ️] Aucun événement à insérer.")
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO events (
            id, action_name, target_type, author_username, 
            created_at, target_title, target_id, 
            project_id, author_id
        )
        VALUES (
            %(id)s, %(action_name)s, %(target_type)s, %(author_username)s,
            %(created_at)s, %(target_title)s, %(target_id)s,
            %(project_id)s, %(author_id)s
        )
        ON CONFLICT (id) DO NOTHING;
        """

        success_count = 0
        for event in events:
            if not all(k in event for k in ("id", "created_at", "action_name")):
                print(f"[⚠️] Événement ignoré : clé(s) manquante(s) dans {event}")
                continue

            try:
                event_data = {
                    "id": event["id"],
                    "action_name": event.get("action_name"),
                    "target_type": event.get("target_type"),
                    "author_username": event.get("author_username"),
                    "created_at": datetime.fromisoformat(event["created_at"]) if event.get("created_at") else None,
                    "target_title": event.get("target_title"),
                    "target_id": event.get("target_id"),
                    "project_id": event.get("project_id"),
                    "author_id": event.get("author_id"),
                }

                cursor.execute(insert_query, event_data)
                success_count += 1

            except Exception as e:
                print(f"[⚠️] Erreur lors de l'insertion de l'événement ID={event.get('id')} : {str(e)}")

        conn.commit()
        print(f"[✅] {success_count}/{len(events)} événements insérés avec succès.")

    except Exception as e:
        print(f"[❌] Erreur lors de la connexion ou l'insertion : {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

