import os
import json
import sys
from datetime import datetime
# Assure l'import 'src.*' en ajoutant la racine du projet
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from src.loaders.database.db_connection import get_db_connection  # adapte si nécessaire

def load_branches(json_path="data/transformers/branches_transformed.json"):
    """Charge et insère les branches depuis un fichier JSON vers la base de données."""
    if not os.path.isabs(json_path):
        json_path = os.path.join(PROJECT_ROOT, json_path)
    if not os.path.exists(json_path):
        print(f"[❌] Fichier introuvable : {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        branches = json.load(f)

    if not branches:
        print("[ℹ️] Aucune branche à insérer.")
        return

    try:
        conn = None
        cursor = None
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO branches (
            name, commit_id, commit_message, created_at, web_url
        )
        VALUES (
            %(name)s, %(commit_id)s, %(commit_message)s, %(created_at)s, %(web_url)s
        )
        ON CONFLICT (name, commit_id) DO NOTHING;
        """

        success_count = 0
        for branch in branches:
            if not all(k in branch for k in ("name", "commit_id", "created_at")):
                print(f"[⚠️] Branche ignorée : clé(s) manquante(s) dans {branch}")
                continue

            try:
                branch_data = {
                    "name": branch["name"],
                    "commit_id": branch.get("commit_id"),
                    "commit_message": branch.get("commit_message"),
                    "created_at": datetime.fromisoformat(branch["created_at"]) if branch.get("created_at") else None,
                    "web_url": branch.get("web_url")
                }

                cursor.execute(insert_query, branch_data)
                success_count += 1

            except Exception as e:
                print(f"[⚠️] Erreur lors de l'insertion de la branche {branch.get('name')} : {str(e)}")

        conn.commit()
        print(f"[✅] {success_count}/{len(branches)} branches insérées avec succès.")

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
    json_path = os.path.join(PROJECT_ROOT, "data", "transformers", "branches_transformed.json")
    load_branches(json_path)