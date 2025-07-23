"""
Package de domaine pour le projet DevOps ETL.

Ce package contient les entités, objets de valeur, services et ports
qui constituent le cœur métier de l'application DevOps ETL.
"""

# Exposer les classes depuis le fichier entities.py directement
from src.domain.entities import (
    Project, Developer, CodeQualityMetric, Commit, SecurityVulnerability
)

# Exposer les objets de valeur
from src.domain.value_objects import (
    DateRange, CommitActivity, MetricValue, CodeCoverage, TechnicalDebt, ProjectIdentifier
)

# Exposer les services
# Note: Déplacé après les imports d'entités pour éviter les imports circulaires
from src.domain.services import ProjectAnalysisService, TeamAnalysisService

__all__ = [
    # Entités
    'Project', 'Developer', 'CodeQualityMetric', 'Commit', 'SecurityVulnerability',
    
    # Objets de valeur
    'DateRange', 'CommitActivity', 'MetricValue', 'CodeCoverage', 'TechnicalDebt', 'ProjectIdentifier',
    
    # Services
    'ProjectAnalysisService', 'TeamAnalysisService',
]
