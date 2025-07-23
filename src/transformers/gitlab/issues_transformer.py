from typing import Any, Dict, List, Optional
from datetime import datetime
from ..base_transformer import BaseTransformer

class IssuesTransformer(BaseTransformer):
    """
    Transformateur pour les issues GitLab, hérite de BaseTransformer.
    """
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        transformed = []
        for issue in data:
            # Gestion robuste des dates
            def parse_date(date_str, fmt):
                if not date_str:
                    return None
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    return None

            created_at = parse_date(issue.get("created_at"), "%Y-%m-%dT%H:%M:%S.%fZ") or parse_date(issue.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")
            updated_at = parse_date(issue.get("updated_at"), "%Y-%m-%dT%H:%M:%S.%fZ") or parse_date(issue.get("updated_at"), "%Y-%m-%dT%H:%M:%SZ")
            due_date = parse_date(issue.get("due_date"), "%Y-%m-%d")

            transformed_issue = {
                "id": issue.get("id"),
                "title": issue.get("title"),
                "state": issue.get("state"),
                "created_at": created_at,
                "updated_at": updated_at,
                "author": issue.get("author", {}).get("name"),
                "web_url": issue.get("web_url"),
                "labels": issue.get("labels", []),
                "assignees": [assignee.get("name") for assignee in issue.get("assignees", [])],
                "due_date": due_date,
                "confidential": issue.get("confidential", False)
            }
            # Ajouter d'autres champs si nécessaire
            transformed.append(transformed_issue)
        return transformed