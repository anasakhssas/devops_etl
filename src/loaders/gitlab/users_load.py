# src/loaders/load_users.py

import json
import os
import sys

# Assure l'import 'src.*' en ajoutant la racine du projet
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.loaders.database.db_connection import get_db_connection


def load_users(json_path="data/transformers/users_transformed.json"):
    # Normalise le chemin du JSON depuis la racine du projet si relatif
    if not os.path.isabs(json_path):
        json_path = os.path.join(PROJECT_ROOT, json_path)

    if not os.path.exists(json_path):
        print(f"[❌] Fichier introuvable : {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        users = json.load(f)

    if not users:
        print("[ℹ️] Aucun utilisateur à insérer.")
        return

    try:
        conn = None
        cursor = None
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO users (
            id, name, username, email, is_admin, state, 
            created_at, last_activity_on, web_url
        )
        VALUES (
            %(id)s, %(name)s, %(username)s, %(email)s, %(is_admin)s, %(state)s, 
            %(created_at)s, %(last_activity_on)s, %(web_url)s
        )
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            username = EXCLUDED.username,
            email = COALESCE(EXCLUDED.email, users.email),
            is_admin = EXCLUDED.is_admin,
            state = EXCLUDED.state,
            created_at = EXCLUDED.created_at,
            last_activity_on = EXCLUDED.last_activity_on,
            web_url = EXCLUDED.web_url;
        """

        for user in users:
            cursor.execute(insert_query, user)

        conn.commit()
        print(f"[✅] {len(users)} utilisateurs insérés/actualisés avec succès.")

    except Exception as e:
        print(f"[❌] Erreur lors de l'insertion des utilisateurs : {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Optionnel : test local
if __name__ == "__main__":
    # Utilise le chemin absolu depuis la racine du projet
    json_path = os.path.join(PROJECT_ROOT, "data", "transformers", "users_transformed.json")
    load_users(json_path)