import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.loaders.database.db_connection import get_db_connection

def load_pipelines(json_path="data/transformers/pipelines_transformed.json"):
    if not os.path.exists(json_path):
        print(f"[❌] Fichier introuvable : {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        pipelines = json.load(f)

    if not pipelines:
        print("[ℹ️] Aucun pipeline à insérer.")
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO pipelines (
            id, project_id, status, source, created_at, updated_at, web_url
        )
        VALUES (
            %(id)s, %(project_id)s, %(status)s, %(source)s, %(created_at)s, %(updated_at)s, %(web_url)s
        )
        ON CONFLICT (id) DO UPDATE SET
            project_id = EXCLUDED.project_id,
            status = EXCLUDED.status,
            source = EXCLUDED.source,
            created_at = EXCLUDED.created_at,
            updated_at = EXCLUDED.updated_at,
            web_url = EXCLUDED.web_url;
        """

        for pipeline in pipelines:
            cursor.execute(insert_query, pipeline)

        conn.commit()
        print(f"[✅] {len(pipelines)} pipelines insérés/actualisés avec succès.")

    except Exception as e:
        print(f"[❌] Erreur lors de l'insertion des pipelines : {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()