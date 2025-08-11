# projects_transformer.py
from typing import List, Dict, Any
from .base_transformer import BaseTransformer

class ProjectsTransformer(BaseTransformer):
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        transformed = []
        for project in data:
            transformed.append({
                "project_key": project.get("key"),
                "project_name": project.get("name"),
                "visibility": project.get("visibility", "private").lower(),
                "last_analysis": project.get("lastAnalysisDate"),
                "tags": ",".join(project.get("tags", [])),
                "qualifier": project.get("qualifier")
            })
        return transformed
