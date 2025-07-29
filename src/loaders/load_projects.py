import os
import json
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from database.db_connection import get_db_connection

REQUIRED_KEYS = ["id", "name", "created_at", "web_url", "namespace", "visibility", "default_branch"]

def insert_projects(conn, projects):
    with conn.cursor() as cur:
        for project in projects:
            if not all(key in project for key in REQUIRED_KEYS):
                print(f"[⚠️] Projet ignoré : clé(s) manquante(s) dans {project}")
                continue
            try:
                cur.execute("""
                    INSERT INTO projects (
                        id, name, description, created_at,
                        web_url, namespace, visibility, default_branch
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                """, (
                    project["id"],
                    project.get("name"),
                    project.get("description"),
                    datetime.fromisoformat(project["created_at"]) if project.get("created_at") else None,
                    project.get("web_url"),
                    project.get("namespace"),
                    project.get("visibility"),
                    project.get("default_branch")
                ))
            except Exception as e:
                print(f"[❌] Erreur lors de l'insertion du projet ID={project.get('id')} : {e}")
        conn.commit()

def main():
    load_dotenv()
    input_path = "data/transformers/projects_transformed.json"
    if not os.path.exists(input_path):
        print(f"[ERREUR] Fichier JSON non trouvé : {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        projects = json.load(f)

    conn = get_db_connection()
    insert_projects(conn, projects)
    conn.close()
    print("✅ Données des projets insérées avec succès dans la base de données.")

if __name__ == "__main__":
    main()
