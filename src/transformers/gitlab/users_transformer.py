from typing import Any, Dict, List, Optional
from datetime import datetime
from ..base_transformer import BaseTransformer

class UsersTransformer(BaseTransformer):
    """
    Transformateur pour les utilisateurs GitLab, hérite de BaseTransformer.
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
        for user in data:
            created_at = parse_date(user.get("created_at"), "%Y-%m-%dT%H:%M:%S.%fZ") or parse_date(user.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")
            transformed_user = {
                "id": user.get("id"),
                "name": user.get("name"),
                "username": user.get("username"),
                "email": user.get("email"),
                "is_admin": user.get("is_admin", False),
                "state": user.get("state"),
                "created_at": created_at,
                "last_activity_on": user.get("last_activity_on"),
                "web_url": user.get("web_url")
            }
            # Ajouter d'autres champs si nécessaire
            transformed.append(transformed_user)
        return transformed