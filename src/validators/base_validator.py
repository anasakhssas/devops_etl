
from abc import ABC, abstractmethod
from typing import Any

class BaseValidator(ABC):
    """
    Classe de base abstraite pour les validateurs de données.
    """
    @abstractmethod
    def validate(self, data: Any) -> bool:
        """
        Valide les données. Doit lever une exception ou retourner False si invalide.
        """
        pass
