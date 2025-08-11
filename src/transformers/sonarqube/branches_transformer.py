# branches_transformer.py
from typing import List, Dict
from .base_transformer import BaseTransformer

class BranchesTransformer(BaseTransformer):
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        transformed = []
        for branch in data:
            transformed.append({
                "name": branch.get("name"),
                "is_main": branch.get("isMain", False),
                "analysis_date": branch.get("analysisDate"),
                "status": branch.get("status", {}).get("qualityGateStatus"),
            })
        return transformed
