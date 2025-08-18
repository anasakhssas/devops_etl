import json
import os
import sys
from datetime import datetime
# Assure l'import 'src.*' en ajoutant la racine du projet
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from src.loaders.database.db_connection import get_db_connection

def load_pipelines(json_path="data/transformers/pipelines_transformed.json"):
    if not os.path.isabs(json_path):
        json_path = os.path.join(PROJECT_ROOT, json_path)
    if not os.path.exists(json_path):
        print(f"[❌] Fichier introuvable : {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        pipelines = json.load(f)

    print(f"[DEBUG] Nombre de pipelines chargés : {len(pipelines)}")  # Ajout debug

    if not pipelines:
        print("[ℹ️] Aucun pipeline à insérer.")
        return

    try:
        conn = None
        cursor = None
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO pipelines (
            id, project_id, status, ref, sha, created_at, updated_at, web_url, username, duration
        )
        VALUES (
            %(id)s, %(project_id)s, %(status)s, %(ref)s, %(sha)s, %(created_at)s, %(updated_at)s, %(web_url)s, %(username)s, %(duration)s
        )
        ON CONFLICT (id) DO UPDATE SET
            project_id = EXCLUDED.project_id,
            status = EXCLUDED.status,
            ref = EXCLUDED.ref,
            sha = EXCLUDED.sha,
            created_at = EXCLUDED.created_at,
            updated_at = EXCLUDED.updated_at,
            web_url = EXCLUDED.web_url,
            username = EXCLUDED.username,
            duration = EXCLUDED.duration;
        """

        success_count = 0  # Ajout compteur
        # Affiche le schéma des colonnes de la table pipelines
        cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'pipelines';")
        columns = cursor.fetchall()
        print("[DEBUG] Colonnes de la table pipelines:", columns)

        for pipeline in pipelines:
            # Conversion explicite des dates si nécessaire
            def parse_date(date_str):
                if not date_str:
                    return None
                try:
                    return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except Exception:
                    return date_str  # Laisse tel quel si déjà au bon format ou string

            pipeline_data = {
                "id": pipeline.get("id"),
                "project_id": pipeline.get("project_id"),
                "status": pipeline.get("status"),
                "ref": pipeline.get("ref"),
                "sha": pipeline.get("sha"),
                "created_at": parse_date(pipeline.get("created_at")),
                "updated_at": parse_date(pipeline.get("updated_at")),
                "web_url": pipeline.get("web_url"),
                "username": pipeline.get("user"),  # Remplace 'user' par 'username'
                "duration": pipeline.get("duration"),
            }
            print("[DEBUG] pipeline brut:", pipeline)
            print("[DEBUG] pipeline_data:", pipeline_data)
            for k, v in pipeline_data.items():
                print(f"[DEBUG] Champ: {k}, Valeur: {v}, Type: {type(v)}")
            try:
                cursor.execute(insert_query, pipeline_data)
                print("[DEBUG] Insertion OK pour id:", pipeline_data["id"])
                success_count += 1
            except Exception as e:
                print(f"[⚠️] Erreur lors de l'insertion du pipeline id={pipeline_data['id']} : {e}")

        conn.commit()
        print(f"[✅] {success_count}/{len(pipelines)} pipelines insérés/actualisés avec succès.")

        # Affiche le contenu de la table pipelines après insertion
        cursor.execute("SELECT * FROM pipelines LIMIT 5;")
        rows = cursor.fetchall()
        print("[DEBUG] Extrait de la table pipelines après insertion:", rows)

    except Exception as e:
        print(f"[❌] Erreur lors de l'insertion des pipelines : {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    # Exécution directe pour tester le chargement des pipelines
    json_path = os.path.join(PROJECT_ROOT, "data", "transformers", "pipelines_transformed.json")
    load_pipelines(json_path)