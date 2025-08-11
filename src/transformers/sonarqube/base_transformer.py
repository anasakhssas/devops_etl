# base_transformer.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseTransformer(ABC):
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    @abstractmethod
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transforme une liste de dictionnaires en appliquant un nettoyage et un formatage.
        """
        pass

    def _strip_strings(self, record: Dict[str, Any]) -> Dict[str, Any]:
        return {k: (v.strip() if isinstance(v, str) else v) for k, v in record.items()}
