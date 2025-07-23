from typing import Any, Dict, List, Optional
from datetime import datetime
from ..base_transformer import BaseTransformer

class ProjectsTransformer(BaseTransformer):
    """
    Transformateur pour les projets GitLab, hérite de BaseTransformer.
    """
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        def parse_date(date_str, fmt):
            if not date_str:
                return None
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                return None

        transformed = []
        for project in data:
            created_at = parse_date(project.get("created_at"), "%Y-%m-%dT%H:%M:%S.%fZ") or parse_date(project.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")
            transformed_project = {
                "id": project.get("id"),
                "name": project.get("name"),
                "description": project.get("description"),
                "created_at": created_at,
                "web_url": project.get("web_url"),
                "namespace": project.get("namespace", {}).get("name"),
                "visibility": project.get("visibility"),
                "default_branch": project.get("default_branch")
            }
            # Ajouter d'autres champs si nécessaire
            transformed.append(transformed_project)
        return transformed