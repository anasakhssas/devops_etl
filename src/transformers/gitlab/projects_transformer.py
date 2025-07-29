from typing import Any, Dict, List
from datetime import datetime

try:
    from ..base_transformer import BaseTransformer
except ImportError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from base_transformer import BaseTransformer

class ProjectsTransformer(BaseTransformer):
    """
    Transformateur pour les projets GitLab avec normalisation des noms de clés.
    """
    # Dictionnaire de correspondance entre les noms incorrects et ceux attendus
    KEY_MAPPING = {
        "ID Projet": "id",
        "Nom Project": "name",
        "URL Projet": "web_url",
        "http url au repo": "http_url_to_repo",
        "Chemin Complet": "path_with_namespace",
        "Groupe Racine": "namespace",
        "Visibilité": "visibility",
        "Archivé": "archived",
        "Créé le": "created_at",
        "Dernière activité": "last_activity_at",
        "default branch": "default_branch",
        "description": "description"
    }

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
                    return date_str  # retourne brut si non transformable

        fields_to_extract = fields or [
            "id", "name", "description", "created_at", "web_url",
            "namespace", "visibility", "default_branch"
        ]

        transformed = []
        for project in data:
            transformed_project = {}
            # Appliquer le mapping pour corriger les clés
            normalized_project = {
                self.KEY_MAPPING.get(k, k): v for k, v in project.items()
            }
            for field in fields_to_extract:
                if field == "created_at":
                    transformed_project["created_at"] = parse_date(normalized_project.get("created_at"))
                elif field == "namespace" and isinstance(normalized_project.get("namespace"), dict):
                    transformed_project["namespace"] = normalized_project.get("namespace", {}).get("name")
                else:
                    transformed_project[field] = normalized_project.get(field)
            # Vérification que toutes les clés sont présentes
            if all(k in transformed_project for k in fields_to_extract):
                transformed.append(transformed_project)
            else:
                print(f"[⚠️] Projet ignoré : clé(s) manquante(s) dans {project}")
        return transformed

if __name__ == "__main__":
    import json

    input_json_path = "data/output/projects.json"
    output_json_path = "data/transformers/projects_transformed.json"

    with open(input_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    transformer = ProjectsTransformer()
    fields_to_extract = [
        "id", "name", "description", "created_at", "web_url",
        "namespace", "visibility", "default_branch"
    ]
    transformed = transformer.transform(data, fields=fields_to_extract)

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(transformed, f, default=str, ensure_ascii=False, indent=2)
