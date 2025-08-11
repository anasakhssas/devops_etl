# issues_transformer.py
from typing import List, Dict
from .base_transformer import BaseTransformer

class IssuesTransformer(BaseTransformer):
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        transformed = []
        for issue in data:
            transformed.append({
                "key": issue.get("key"),
                "type": issue.get("type"),
                "severity": issue.get("severity"),
                "status": issue.get("status"),
                "creation_date": issue.get("creationDate"),
                "update_date": issue.get("updateDate"),
                "component": issue.get("component"),
                "project": issue.get("project")
            })
        return transformed
