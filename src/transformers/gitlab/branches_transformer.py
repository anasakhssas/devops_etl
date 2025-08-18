from typing import List, Dict, Any
from datetime import datetime

class BranchesTransformer:
    """
    Transformateur pour les branches GitLab.
    """
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        def parse_date(date_str):
            if not date_str:
                return None
            try:
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                try:
                    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    return None

        transformed = []
        for branch in data:
            created_at = branch.get("created_at")
            dt = parse_date(created_at)
            transformed_branch = {
                "name": branch.get("name"),
                "commit_id": branch.get("commit", {}).get("id"),
                "commit_message": branch.get("commit", {}).get("message"),
                "created_at": dt,
                "web_url": branch.get("web_url"),
                "project_id": int(branch.get("project_id")) if branch.get("project_id") is not None else None,  # ajout ici
            }
            transformed.append(transformed_branch)
        return transformed

if __name__ == "__main__":
    import json
    import os

    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_json_path = os.path.abspath(os.path.join(base_dir, "../../../data/output/projects_branches_incremental.json"))
    output_json_path = os.path.abspath(os.path.join(base_dir, "../../../data/transformers/branches_transformed.json"))

    if not os.path.exists(input_json_path):
        print(f"[ERREUR] Fichier introuvable : {input_json_path}")
        exit(1)

    with open(input_json_path, "r", encoding="utf-8") as f:
        projects_branches = json.load(f)

    # Fusionner toutes les branches de tous les projets dans une seule liste
    all_branches = []
    for branches_list in projects_branches.values():
        all_branches.extend(branches_list)

    transformer = BranchesTransformer()
    transformed = transformer.transform(all_branches)

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(transformed, f, default=str, ensure_ascii=False, indent=2)
