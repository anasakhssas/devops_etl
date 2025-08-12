import os
import json
import sys
from datetime import datetime
# Assure l'import 'src.*' en ajoutant la racine du projet
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from src.loaders.database.db_connection import get_db_connection

def load_merge_requests(json_path="data/transformers/merge_requests_transformed.json"):
    print(f"[DEBUG] Appel de load_merge_requests avec json_path={json_path}")
    """Charge et insère les merge requests depuis un fichier JSON vers la base de données."""
    if not os.path.isabs(json_path):
        json_path = os.path.join(PROJECT_ROOT, json_path)
    if not os.path.exists(json_path):
        print(f"[❌] Fichier introuvable : {json_path}")
        return

    print(f"[DEBUG] Fichier trouvé : {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        merge_requests = json.load(f)

    print(f"[DEBUG] Nombre de merge requests chargées : {len(merge_requests)}")
    if not merge_requests:
        print("[ℹ️] Aucune merge request à insérer.")
        return

    try:
        conn = None
        cursor = None
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO merge_requests (
            id, title, state, created_at, updated_at,
            author, web_url, source_branch, target_branch, merged_at
        )
        VALUES (
            %(id)s, %(title)s, %(state)s, %(created_at)s, %(updated_at)s,
            %(author)s, %(web_url)s, %(source_branch)s, %(target_branch)s, %(merged_at)s
        )
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            state = EXCLUDED.state,
            created_at = EXCLUDED.created_at,
            updated_at = EXCLUDED.updated_at,
            author = EXCLUDED.author,
            web_url = EXCLUDED.web_url,
            source_branch = EXCLUDED.source_branch,
            target_branch = EXCLUDED.target_branch,
            merged_at = EXCLUDED.merged_at;
        """

        success_count = 0
        for mr in merge_requests:
            try:
                # Formatage des dates
                try:
                    if mr.get("created_at") and not isinstance(mr["created_at"], datetime):
                        mr["created_at"] = datetime.fromisoformat(mr["created_at"])
                    if mr.get("updated_at") and not isinstance(mr["updated_at"], datetime):
                        mr["updated_at"] = datetime.fromisoformat(mr["updated_at"])
                    if mr.get("merged_at") and not isinstance(mr["merged_at"], datetime):
                        mr["merged_at"] = datetime.fromisoformat(mr["merged_at"])
                except Exception as date_exc:
                    print(f"[⚠️] Erreur de format de date sur MR ID={mr.get('id')} : {str(date_exc)}")
                    continue

                if not all(k in mr for k in ("id", "title", "created_at")) or mr["created_at"] is None:
                    print(f"[⚠️] Merge request ignorée : clé(s) manquante(s) ou 'created_at' invalide dans {mr.get('id')}")
                    continue

                cursor.execute(insert_query, mr)
                success_count += 1
            except Exception as e:
                print(f"[⚠️] Erreur sur MR ID={mr.get('id')} : {str(e)}")

        conn.commit()
        print(f"[✅] {success_count}/{len(merge_requests)} merge requests insérées/actualisées avec succès.")

    except Exception as e:
        print(f"[❌] Erreur globale lors de l'insertion des merge requests : {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

# Optionnel : test local
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(PROJECT_ROOT, "data", "transformers", "merge_requests_transformed.json")
    load_merge_requests(json_path)

