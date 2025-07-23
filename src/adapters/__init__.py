"""
Module d'initialisation pour les adaptateurs.

Ce package contient les implémentations des adaptateurs pour
les différentes sources de données et services externes.
"""

# Import pour faciliter l'accès aux adaptateurs
from src.adapters.gitlab import (
    GitLabProjectRepository,
    GitLabDeveloperRepository,
    GitLabCommitRepository,
    GitLabClient
)

__all__ = [
    # Adaptateurs GitLab
    'GitLabProjectRepository',
    'GitLabDeveloperRepository',
    'GitLabCommitRepository',
    'GitLabClient',
]
