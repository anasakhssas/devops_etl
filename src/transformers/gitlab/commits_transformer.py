from typing import Any, Dict, List, Optional
from datetime import datetime
from ..base_transformer import BaseTransformer

class CommitsTransformer(BaseTransformer):
    """
    Transformateur pour les commits GitLab, hérite de BaseTransformer.
    """
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        transformed = []
        for commit in data:
            created_at = commit.get("created_at")
            dt = None
            if created_at:
                try:
                    dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError:
                    try:
                        dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
                    except ValueError:
                        dt = None
            transformed_commit = {
                "id": commit.get("id"),
                "short_id": commit.get("short_id"),
                "title": commit.get("title"),
                "author_name": commit.get("author_name"),
                "author_email": commit.get("author_email"),
                "created_at": dt,
                "message": commit.get("message"),
                "web_url": commit.get("web_url")
            }
            # Ajouter d'autres champs si nécessaire
            transformed.append(transformed_commit)
        return transformed