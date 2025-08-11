# quality_gate_transformer.py
from typing import List, Dict, Any
from .base_transformer import BaseTransformer

class QualityGateTransformer(BaseTransformer):
    def transform(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [{
            "status": data.get("projectStatus", {}).get("status"),
            "conditions": data.get("projectStatus", {}).get("conditions", [])
        }]
