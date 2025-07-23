from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseTransformer(ABC):
    """
      Classe abstraite pour les transformateurs de données.
    Chaque transformateur prend des données brutes extraites et les transforme pour un usage analytique.
    """
    def __init__(self, config: Dict[str, Any] = {}):
        """
        Initialise le transformateur avec une configuration optionnelle.

        Args:
            config: Dictionnaire de configuration.
        """
        self.config = config

    @abstractmethod
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transforme les données brutes extraites en données prêtes pour l'analyse.

        Args:
            data: Liste de dictionnaires représentant les données brutes.

        Returns:
            Liste de dictionnaires représentant les données transformées.
        """
        pass

    def validate(self, data: List[Dict[str, Any]]) -> bool:
        """
        Valide les données transformées (optionnel).

        Args:
            data: Liste de dictionnaires représentant les données transformées.

        Returns:
            bool: True si les données sont valides, False sinon.
        """
        return True
        