from typing import List, Dict, Any
from datetime import datetime
from ..base_transformer import BaseTransformer
"""
Module de transformation des merge requests GitLab.
"""
class MergeRequestsTransformer(BaseTransformer):
    """
    Transformateur pour les merge requests GitLab, hérite de BaseTransformer.
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
        for mr in data:
            created_at = parse_date(mr.get("created_at"), "%Y-%m-%dT%H:%M:%S.%fZ") or parse_date(mr.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")
            updated_at = parse_date(mr.get("updated_at"), "%Y-%m-%dT%H:%M:%S.%fZ") or parse_date(mr.get("updated_at"), "%Y-%m-%dT%H:%M:%SZ")
            merged_at = parse_date(mr.get("merged_at"), "%Y-%m-%dT%H:%M:%S.%fZ") or parse_date(mr.get("merged_at"), "%Y-%m-%dT%H:%M:%SZ") if mr.get("state") == "merged" else None
            transformed_mr = {
                "id": mr.get("id"),
                "title": mr.get("title"),
                "state": mr.get("state"),
                "created_at": created_at,
                "updated_at": updated_at,
                "author": mr.get("author", {}).get("name"),
                "web_url": mr.get("web_url"),
                "source_branch": mr.get("source_branch"),
                "target_branch": mr.get("target_branch"),
                "merged_at": merged_at
            }
            # Ajouter d'autres champs si nécessaire
            transformed.append(transformed_mr)
        return transformed