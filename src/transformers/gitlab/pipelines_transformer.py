from typing import Any, Dict, List, Optional
from datetime import datetime
from ..base_transformer import BaseTransformer
class PipelinesTransformer(BaseTransformer):
    """
    Transformateur pour les pipelines GitLab, hérite de BaseTransformer.
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
        for pipeline in data:
            created_at = parse_date(pipeline.get("created_at"), "%Y-%m-%dT%H:%M:%S.%fZ") or parse_date(pipeline.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")
            updated_at = parse_date(pipeline.get("updated_at"), "%Y-%m-%dT%H:%M:%S.%fZ") or parse_date(pipeline.get("updated_at"), "%Y-%m-%dT%H:%M:%SZ")
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
            # Ajouter d'autres champs si nécessaire
            transformed.append(transformed_pipeline)
        return transformed