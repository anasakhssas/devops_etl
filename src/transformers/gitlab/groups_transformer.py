from typing import List, Dict, Any
from datetime import datetime
from ..base_transformer import BaseTransformer

class GroupsTransformer(BaseTransformer):
    """
    Transformateur pour les groupes GitLab, hérite de BaseTransformer.
    """
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        transformed = []
        for group in data:
            created_at = group.get("created_at")
            dt = None
            if created_at:
                try:
                    dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError:
                    try:
                        dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
                    except ValueError:
                        dt = None
            transformed_group = {
                "id": group.get("id"),
                "name": group.get("name"),
                "path": group.get("path"),
                "description": group.get("description"),
                "visibility": group.get("visibility"),
                "created_at": dt,
                "web_url": group.get("web_url"),
                "avatar_url": group.get("avatar_url")
            }
            # Ajouter d'autres champs si nécessaire
            transformed.append(transformed_group)
        return transformed