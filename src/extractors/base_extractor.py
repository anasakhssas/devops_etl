"""
Module définissant la classe de base pour tous les extracteurs de données.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.core.exceptions import ExtractionError


class BaseExtractor(ABC):
    """
    Classe abstraite définissant l'interface pour tous les extracteurs.
    Les extracteurs sont responsables de récupérer les données depuis les sources externes.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialise l'extracteur avec la configuration fournie.
        
        Args:
            config: Dictionnaire de configuration pour l'extracteur.
        """
        self.config = config
        self.is_connected = False

    @abstractmethod
    def connect(self) -> bool:
        """
        Établit la connexion avec la source de données.
        
        Returns:
            True si la connexion est réussie, False sinon.
            
        Raises:
            ExtractionError: Si une erreur survient lors de la connexion.
        """
        pass

    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """
        Teste la connexion à la source de données.
        
        Returns:
            Dictionnaire contenant des informations sur le statut de la connexion.
            
        Raises:
            ExtractionError: Si une erreur survient lors du test de connexion.
        """
        pass

    @abstractmethod
    def extract(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Extrait les données depuis la source.
        
        Args:
            **kwargs: Paramètres spécifiques à l'extracteur.
            
        Returns:
            Liste de dictionnaires représentant les données extraites.
            
        Raises:
            ExtractionError: Si une erreur survient lors de l'extraction.
        """
        pass

    def extract_incremental(self, from_date: str, to_date: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Extrait les données de manière incrémentielle depuis la source.
        
        Args:
            from_date: Date de début au format YYYY-MM-DD.
            to_date: Date de fin optionnelle au format YYYY-MM-DD.
            **kwargs: Paramètres spécifiques à l'extracteur.
            
        Returns:
            Liste de dictionnaires représentant les données extraites.
            
        Raises:
            ExtractionError: Si une erreur survient lors de l'extraction.
        """
        raise NotImplementedError("Cette méthode doit être implémentée par les sous-classes.")

    def close(self) -> None:
        """
        Ferme la connexion à la source de données.
        """
        self.is_connected = False
