from typing import Any, Dict, List
from datetime import datetime
import os

class CommitsTransformer:
    """
    Transformateur pour les commits GitLab.
    """
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        transformed = []
        for commit in data:
            created_at = commit.get("created_at")
            dt = None
            if created_at:
                try:
                    dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError:
                    try:
                        dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
                    except ValueError:
                        dt = None
            transformed_commit = {
                "id": commit.get("id"),
                "short_id": commit.get("short_id"),
                "title": commit.get("title"),
                "author_name": commit.get("author_name"),
                "author_email": commit.get("author_email"),
                "created_at": dt,
                "message": commit.get("message"),
                "web_url": commit.get("web_url")
            }
            transformed.append(transformed_commit)
        return transformed

if __name__ == "__main__":
    import json

    # Construction du chemin absolu depuis ce script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_json_path = os.path.abspath(os.path.join(base_dir, "../../../data/output/projects_commits_incremental.json"))
    output_json_path = os.path.abspath(os.path.join(base_dir, "../../../data/transformers/commits_transformed.json"))

    if not os.path.exists(input_json_path):
        print(f"[ERREUR] Fichier introuvable : {input_json_path}")
        exit(1)

    with open(input_json_path, "r", encoding="utf-8") as f:
        projects_commits = json.load(f)

    # Fusionner tous les commits de tous les projets dans une seule liste
    all_commits = []
    for commits_list in projects_commits.values():
        all_commits.extend(commits_list)

    transformer = CommitsTransformer()
    transformed = transformer.transform(all_commits)

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(transformed, f, default=str, ensure_ascii=False, indent=2)
