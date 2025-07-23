"""
Interfaces de services externes pour le pattern Hexagonal/Ports & Adapters.

Ce module définit les interfaces abstraites (ports) que les adaptateurs
devront implémenter pour fournir des services techniques externes au domaine.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from enum import Enum


class LogLevel(Enum):
    """Niveaux de log supportés."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class NotificationService(ABC):
    """Interface pour les services de notification."""
    
    @abstractmethod
    def send_notification(self, recipient: str, subject: str, message: str) -> bool:
        """
        Envoie une notification à un destinataire.
        
        Args:
            recipient: Destinataire de la notification (email, identifiant, etc.)
            subject: Sujet de la notification
            message: Corps du message
            
        Returns:
            True si la notification a été envoyée avec succès, False sinon
        """
        pass
    
    @abstractmethod
    def send_batch_notifications(
        self, notifications: List[Dict[str, str]]
    ) -> Dict[str, bool]:
        """
        Envoie un lot de notifications.
        
        Args:
            notifications: Liste de dictionnaires contenant recipient, subject et message
            
        Returns:
            Dictionnaire avec les destinataires comme clés et les statuts d'envoi comme valeurs
        """
        pass


class CacheService(ABC):
    """Interface pour les services de cache."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """
        Récupère une valeur depuis le cache.
        
        Args:
            key: Clé de la valeur à récupérer
            
        Returns:
            La valeur associée à la clé ou None si elle n'existe pas
        """
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Stocke une valeur dans le cache.
        
        Args:
            key: Clé sous laquelle stocker la valeur
            value: Valeur à stocker
            ttl: Durée de vie en secondes (None pour pas d'expiration)
            
        Returns:
            True si l'opération a réussi, False sinon
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Supprime une valeur du cache.
        
        Args:
            key: Clé de la valeur à supprimer
            
        Returns:
            True si la valeur a été supprimée, False sinon
        """
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """
        Vide le cache.
        
        Returns:
            True si l'opération a réussi, False sinon
        """
        pass


class LoggingService(ABC):
    """Interface pour les services de journalisation."""
    
    @abstractmethod
    def log(self, level: LogLevel, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Enregistre un message de log.
        
        Args:
            level: Niveau de log
            message: Message à enregistrer
            context: Contexte additionnel (optionnel)
        """
        pass
    
    @abstractmethod
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Enregistre un message de debug.
        
        Args:
            message: Message à enregistrer
            context: Contexte additionnel (optionnel)
        """
        pass
    
    @abstractmethod
    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Enregistre un message d'information.
        
        Args:
            message: Message à enregistrer
            context: Contexte additionnel (optionnel)
        """
        pass
    
    @abstractmethod
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Enregistre un avertissement.
        
        Args:
            message: Message à enregistrer
            context: Contexte additionnel (optionnel)
        """
        pass
    
    @abstractmethod
    def error(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Enregistre une erreur.
        
        Args:
            message: Message à enregistrer
            context: Contexte additionnel (optionnel)
        """
        pass
    
    @abstractmethod
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Enregistre une erreur critique.
        
        Args:
            message: Message à enregistrer
            context: Contexte additionnel (optionnel)
        """
        pass
