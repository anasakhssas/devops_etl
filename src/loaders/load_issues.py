import os
import json
from datetime import datetime
from src.loaders.database.db_connection import get_db_connection  # Assure-toi que le chemin est correct

def load_issues(json_path="data/transformers/issues_transformed.json"):
    """Charge et insère les issues depuis un fichier JSON vers la base de données."""

    if not os.path.exists(json_path):
        print(f"[❌] Fichier introuvable : {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        issues = json.load(f)

    if not issues:
        print("[ℹ️] Aucune issue à insérer.")
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO issues (
            id, title, state, created_at, updated_at,
            author, web_url, labels, assignees,
            due_date, confidential
        )
        VALUES (
            %(id)s, %(title)s, %(state)s, %(created_at)s, %(updated_at)s,
            %(author)s, %(web_url)s, %(labels)s, %(assignees)s,
            %(due_date)s, %(confidential)s
        )
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            state = EXCLUDED.state,
            created_at = EXCLUDED.created_at,
            updated_at = EXCLUDED.updated_at,
            author = EXCLUDED.author,
            web_url = EXCLUDED.web_url,
            labels = EXCLUDED.labels,
            assignees = EXCLUDED.assignees,
            due_date = EXCLUDED.due_date,
            confidential = EXCLUDED.confidential;
        """

        success_count = 0
        for issue in issues:
            if not all(k in issue for k in ("id", "title", "created_at")):
                print(f"[⚠️] Issue ignorée : clé(s) manquante(s) dans {issue}")
                continue

            try:
                issue_data = {
                    "id": issue["id"],
                    "title": issue["title"],
                    "state": issue.get("state"),
                    "created_at": datetime.fromisoformat(issue["created_at"]) if issue.get("created_at") else None,
                    "updated_at": datetime.fromisoformat(issue["updated_at"]) if issue.get("updated_at") else None,
                    "author": issue.get("author"),
                    "web_url": issue.get("web_url"),
                    "labels": issue.get("labels", []),
                    "assignees": issue.get("assignees", []),
                    "due_date": datetime.fromisoformat(issue["due_date"]) if issue.get("due_date") else None,
                    "confidential": issue.get("confidential", False)
                }

                cursor.execute(insert_query, issue_data)
                success_count += 1

            except Exception as e:
                print(f"[⚠️] Erreur lors de l'insertion de l'issue ID={issue.get('id')} : {str(e)}")

        conn.commit()
        print(f"[✅] {success_count}/{len(issues)} issues insérées/actualisées avec succès.")

    except Exception as e:
        print(f"[❌] Erreur lors de la connexion ou l'insertion : {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
