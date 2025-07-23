"""
Ports (interfaces) du domaine pour le pattern Hexagonal.

Ce package contient l'ensemble des interfaces que doivent implémenter
les adaptateurs pour communiquer avec le domaine.
"""

from src.domain.ports.repositories import (
    ProjectRepository, DeveloperRepository, CommitRepository,
    CodeQualityRepository, SecurityRepository
)

from src.domain.ports.services import (
    NotificationService, CacheService, LoggingService
)

__all__ = [
    # Ports de repositories
    'ProjectRepository',
    'DeveloperRepository',
    'CommitRepository',
    'CodeQualityRepository',
    'SecurityRepository',
    
    # Ports de services
    'NotificationService',
    'CacheService',
    'LoggingService'
]
