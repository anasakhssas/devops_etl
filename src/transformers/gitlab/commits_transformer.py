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
            # L'API GitLab utilise 'authored_date' ou 'committed_date' pour les commits.
            # 'created_at' est souvent utilisé pour d'autres objets comme les projets ou les issues.
            created_at_str = commit.get("authored_date") or commit.get("committed_date")
            stats = commit.get("stats") or {}
            transformed_commit = {
                "id": commit.get("id"),
                "short_id": commit.get("short_id"),
                "title": commit.get("title"),
                "author_name": commit.get("author_name"),
                "author_email": commit.get("author_email"),
                "created_at": created_at_str, # Garde la date en format ISO string
                "message": commit.get("message"),
                "web_url": commit.get("web_url"),
                "lines_added": stats.get("additions"),
                "lines_deleted": stats.get("deletions"),
                "project_id": int(commit.get("project_id")) if commit.get("project_id") is not None else None,  # conversion explicite
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
    for project_id, commits_list in projects_commits.items():
        for commit in commits_list:
            commit["project_id"] = int(project_id)  # Ajout du project_id comme entier
            all_commits.append(commit)

    transformer = CommitsTransformer()
    transformed = transformer.transform(all_commits)

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(transformed, f, default=str, ensure_ascii=False, indent=2)
