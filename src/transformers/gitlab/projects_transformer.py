from typing import Any, Dict, List
from datetime import datetime

try:
    from ..base_transformer import BaseTransformer
except ImportError:
    # Permet l'exécution directe du fichier pour les tests locaux
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from base_transformer import BaseTransformer

class ProjectsTransformer(BaseTransformer):
    """
    Transformateur pour les projets GitLab, hérite de BaseTransformer.
    """
    def transform(self, data: List[Dict[str, Any]], fields: List[str] = None) -> List[Dict[str, Any]]:
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

        # Liste des champs à extraire (modifiez ici selon vos besoins)
        fields_to_extract = fields or [
            "id", "name", "description", "created_at", "web_url",
            "namespace", "visibility", "default_branch"
        ]

        transformed = []
        for project in data:
            transformed_project = {}
            for field in fields_to_extract:
                if field == "created_at":
                    transformed_project["created_at"] = parse_date(project.get("created_at"))
                elif field == "namespace":
                    transformed_project["namespace"] = project.get("namespace", {}).get("name")
                else:
                    transformed_project[field] = project.get(field)
            transformed.append(transformed_project)
        return transformed

if __name__ == "__main__":
    import json

    # Remplacez ce chemin par le chemin réel de votre fichier JSON extrait
    input_json_path = "../../data/projects.json"
    output_json_path = "../../data/projects_transformed.json"

    with open(input_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    transformer = ProjectsTransformer()
    # Modifiez la liste ici pour extraire d'autres champs si besoin
    fields_to_extract = [
        "id", "name", "description", "created_at", "web_url",
        "namespace", "visibility", "default_branch"
    ]
    transformed = transformer.transform(data, fields=fields_to_extract)

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(transformed, f, default=str, ensure_ascii=False, indent=2)