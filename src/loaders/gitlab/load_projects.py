import json
import os
import sys
# Assure l'import 'src.*' en ajoutant la racine du projet
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from src.loaders.database.db_connection import get_db_connection

def load_projects(json_path="data/transformers/projects_transformed.json"):
    if not os.path.isabs(json_path):
        json_path = os.path.join(PROJECT_ROOT, json_path)
    if not os.path.exists(json_path):
        print(f"[❌] Fichier introuvable : {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        projects = json.load(f)

    if not projects:
        print("[ℹ️] Aucun projet à insérer.")
        return

    try:
        conn = None
        cursor = None
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO projects (
            id, name, description, created_at, web_url, 
            namespace, visibility, default_branch
        )
        VALUES (
            %(id)s, %(name)s, %(description)s, %(created_at)s, %(web_url)s,
            %(namespace)s, %(visibility)s, %(default_branch)s
        )
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            description = EXCLUDED.description,
            created_at = EXCLUDED.created_at,
            web_url = EXCLUDED.web_url,
            namespace = EXCLUDED.namespace,
            visibility = EXCLUDED.visibility,
            default_branch = EXCLUDED.default_branch;
        """

        for project in projects:
            if not all(k in project for k in ("id", "name", "created_at", "web_url")):
                print(f"[⚠️] Projet ignoré : clé(s) manquante(s) dans {project}")
                continue

            cursor.execute(insert_query, project)

        conn.commit()
        print(f"[✅] {len(projects)} projets insérés/actualisés avec succès.")

    except Exception as e:
        print(f"[❌] Erreur lors de l'insertion des projets : {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Optionnel : test local
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(PROJECT_ROOT, "data", "transformers", "projects_transformed.json")
    load_projects(json_path)