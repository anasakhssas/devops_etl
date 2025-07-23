
from typing import Any, Dict, List, Optional
from datetime import datetime
from ..base_transformer import BaseTransformer

class BranchesTransformer(BaseTransformer):
    """
    Transformateur pour les branches GitLab, hérite de BaseTransformer.
    """
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        transformed = []
        for branch in data:
            created_at = branch.get("created_at")
            # Gestion des dates avec ou sans microsecondes
            dt = None
            if created_at:
                try:
                    dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError:
                    try:
                        dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
                    except ValueError:
                        dt = None
            transformed_branch = {
                "name": branch.get("name"),
                "commit_id": branch.get("commit", {}).get("id"),
                "commit_message": branch.get("commit", {}).get("message"),
                "created_at": dt,
                "web_url": branch.get("web_url")
            }
            # Ajouter d'autres champs si nécessaire
            transformed.append(transformed_branch)
        return transformed