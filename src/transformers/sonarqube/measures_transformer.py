# measures_transformer.py
from typing import List, Dict, Any
from .base_transformer import BaseTransformer

class MeasuresTransformer(BaseTransformer):
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        transformed = []
        for m in data:
            transformed.append({
                "metric": m.get("metric"),
                "value": float(m.get("value", 0)) if m.get("value") else None,
                "date": m.get("date")
            })
        return transformed
