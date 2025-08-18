from typing import List, Dict, Any
from datetime import datetime

class MergeRequestsTransformer:
    """
    Transformateur pour les merge requests GitLab.
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
        for mr in data:
            created_at = parse_date(mr.get("created_at"))
            updated_at = parse_date(mr.get("updated_at"))
            merged_at = parse_date(mr.get("merged_at")) if mr.get("state") == "merged" else None
            transformed_mr = {
                "id": mr.get("id"),
                "title": mr.get("title"),
                "state": mr.get("state"),
                "created_at": created_at,
                "updated_at": updated_at,
                "author": mr.get("author", {}).get("name"),
                "web_url": mr.get("web_url"),
                "source_branch": mr.get("source_branch"),
                "target_branch": mr.get("target_branch"),
                "merged_at": merged_at,
                "project_id": int(mr.get("project_id")) if mr.get("project_id") is not None else None,  # ajout ici
            }
            transformed.append(transformed_mr)
        return transformed

if __name__ == "__main__":
    import json
    import os

    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_json_path = os.path.abspath(os.path.join(base_dir, "../../../data/output/projects_merge_requests_incremental.json"))
    output_json_path = os.path.abspath(os.path.join(base_dir, "../../../data/transformers/merge_requests_transformed.json"))

    if not os.path.exists(input_json_path):
        print(f"[ERREUR] Fichier introuvable : {input_json_path}")
        exit(1)

    with open(input_json_path, "r", encoding="utf-8") as f:
        projects_mrs = json.load(f)

    # Fusionner toutes les MR de tous les projets dans une seule liste
    all_mrs = []
    for mrs_list in projects_mrs.values():
        all_mrs.extend(mrs_list)

    transformer = MergeRequestsTransformer()
    transformed = transformer.transform(all_mrs)

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(transformed, f, default=str, ensure_ascii=False, indent=2)