from typing import List, Dict, Any
from datetime import datetime

class PipelinesTransformer:
    """
    Transformateur pour les pipelines GitLab.
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
        for pipeline in data:
            created_at = parse_date(pipeline.get("created_at"))
            updated_at = parse_date(pipeline.get("updated_at"))
            transformed_pipeline = {
                "id": pipeline.get("id"),
                "status": pipeline.get("status"),
                "ref": pipeline.get("ref"),
                "sha": pipeline.get("sha"),
                "created_at": created_at,
                "updated_at": updated_at,
                "web_url": pipeline.get("web_url"),
                "user": pipeline.get("user", {}).get("name"),
                "duration": pipeline.get("duration")
            }
            transformed.append(transformed_pipeline)
        return transformed

if __name__ == "__main__":
    import json
    import os

    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_json_path = os.path.abspath(os.path.join(base_dir, "../../../data/output/projects_pipelines_incremental.json"))
    output_json_path = os.path.abspath(os.path.join(base_dir, "../../../data/transformers/pipelines_transformed.json"))

    if not os.path.exists(input_json_path):
        print(f"[ERREUR] Fichier introuvable : {input_json_path}")
        exit(1)

    with open(input_json_path, "r", encoding="utf-8") as f:
        projects_pipelines = json.load(f)

    # Fusionner tous les pipelines de tous les projets dans une seule liste
    all_pipelines = []
    for pipelines_list in projects_pipelines.values():
        all_pipelines.extend(pipelines_list)

    transformer = PipelinesTransformer()
    transformed = transformer.transform(all_pipelines)

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(transformed, f, default=str, ensure_ascii=False, indent=2)
