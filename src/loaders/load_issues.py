import os
import json
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from database.db_connection import get_db_connection

def insert_issues(conn, issues):
    with conn.cursor() as cur:
        for issue in issues:
            try:
                cur.execute("""
                    INSERT INTO issues (
                        id, title, state, created_at, updated_at,
                        author, web_url, labels, assignees,
                        due_date, confidential
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                """, (
                    issue["id"],
                    issue["title"],
                    issue["state"],
                    issue["created_at"],
                    issue["updated_at"],
                    issue["author"],
                    issue["web_url"],
                    issue["labels"],
                    issue["assignees"],
                    issue["due_date"],
                    issue["confidential"]
                ))
            except Exception as e:
                print(f"[❌] Erreur lors de l'insertion de l'issue ID={issue.get('id')} : {e}")
        conn.commit()

def main():
    load_dotenv()
    input_path = "data/transformers/issues_transformed.json"
    
    if not os.path.exists(input_path):
        print(f"[ERREUR] Fichier JSON introuvable : {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        issues = json.load(f)

    conn = get_db_connection()
    insert_issues(conn, issues)
    conn.close()
    print("✅ Données des issues insérées avec succès dans la base de données.")

if __name__ == "__main__":
    main()
