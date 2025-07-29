import os
import json
from datetime import datetime
from src.loaders.database.db_connection import get_db_connection  # Chemin à adapter si besoin

def load_commits(json_path="data/transformers/commits_transformed.json"):
    """Charge et insère les commits depuis un fichier JSON vers la base de données."""

    if not os.path.exists(json_path):
        print(f"[❌] Fichier introuvable : {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        commits = json.load(f)

    if not commits:
        print("[ℹ️] Aucun commit à insérer.")
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO commits (
            id, short_id, title, author_name, author_email,
            created_at, message, web_url
        )
        VALUES (
            %(id)s, %(short_id)s, %(title)s, %(author_name)s, %(author_email)s,
            %(created_at)s, %(message)s, %(web_url)s
        )
        ON CONFLICT (id) DO NOTHING;
        """

        success_count = 0
        for commit in commits:
            if not all(k in commit for k in ("id", "short_id", "created_at", "message")):
                print(f"[⚠️] Commit ignoré : clé(s) manquante(s) dans {commit}")
                continue

            try:
                commit_data = {
                    "id": commit["id"],
                    "short_id": commit.get("short_id"),
                    "title": commit.get("title"),
                    "author_name": commit.get("author_name"),
                    "author_email": commit.get("author_email"),
                    "created_at": datetime.fromisoformat(commit["created_at"]) if commit.get("created_at") else None,
                    "message": commit.get("message"),
                    "web_url": commit.get("web_url")
                }

                cursor.execute(insert_query, commit_data)
                success_count += 1

            except Exception as e:
                print(f"[⚠️] Erreur lors de l'insertion du commit ID={commit.get('id')} : {str(e)}")

        conn.commit()
        print(f"[✅] {success_count}/{len(commits)} commits insérés avec succès.")

    except Exception as e:
        print(f"[❌] Erreur lors de la connexion ou de l'insertion : {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Optionnel : test local
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "../../data/transformers/commits_transformed.json")
    load_commits(json_path)
