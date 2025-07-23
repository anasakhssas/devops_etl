"""
Interfaces de repositories pour le pattern Hexagonal/Ports & Adapters.

Ce module définit les interfaces abstraites (ports) que les adapters
devront implémenter pour interagir avec les sources de données externes.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from src.domain.entities import Project, Developer, CodeQualityMetric, Commit, SecurityVulnerability
from src.domain.value_objects import DateRange, ProjectIdentifier


class ProjectRepository(ABC):
    """Interface pour l'accès aux données des projets."""
    
    @abstractmethod
    def get_all(self) -> List[Project]:
        """Récupère tous les projets."""
        pass
    
    @abstractmethod
    def get_by_id(self, project_id: ProjectIdentifier) -> Optional[Project]:
        """Récupère un projet par son identifiant."""
        pass
    
    @abstractmethod
    def save(self, project: Project) -> Project:
        """Persiste un projet."""
        pass
    
    @abstractmethod
    def get_projects_by_criteria(self, criteria: Dict[str, Any]) -> List[Project]:
        """Récupère les projets selon des critères spécifiques."""
        pass


class DeveloperRepository(ABC):
    """Interface pour l'accès aux données des développeurs."""
    
    @abstractmethod
    def get_all(self) -> List[Developer]:
        """Récupère tous les développeurs."""
        pass
    
    @abstractmethod
    def get_by_id(self, developer_id: str) -> Optional[Developer]:
        """Récupère un développeur par son identifiant."""
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Developer]:
        """Récupère un développeur par son email."""
        pass
    
    @abstractmethod
    def save(self, developer: Developer) -> Developer:
        """Persiste un développeur."""
        pass
    
    @abstractmethod
    def get_project_members(self, project_id: ProjectIdentifier) -> List[Developer]:
        """Récupère les membres d'un projet spécifique."""
        pass


class CommitRepository(ABC):
    """Interface pour l'accès aux données des commits."""
    
    @abstractmethod
    def get_by_project(self, project_id: ProjectIdentifier, date_range: Optional[DateRange] = None) -> List[Commit]:
        """Récupère les commits d'un projet, optionnellement filtrés par date."""
        pass
    
    @abstractmethod
    def get_by_developer(self, developer_id: str, date_range: Optional[DateRange] = None) -> List[Commit]:
        """Récupère les commits d'un développeur, optionnellement filtrés par date."""
        pass
    
    @abstractmethod
    def save(self, commit: Commit) -> Commit:
        """Persiste un commit."""
        pass
    
    @abstractmethod
    def get_commit_stats(self, project_id: ProjectIdentifier, date_range: DateRange) -> Dict[str, Any]:
        """Récupère des statistiques sur les commits d'un projet pour une période donnée."""
        pass


class CodeQualityRepository(ABC):
    """Interface pour l'accès aux données de qualité du code."""
    
    @abstractmethod
    def get_metrics_by_project(self, project_id: ProjectIdentifier) -> List[CodeQualityMetric]:
        """Récupère les métriques de qualité du code pour un projet."""
        pass
    
    @abstractmethod
    def get_metric_history(
        self, project_id: ProjectIdentifier, metric_name: str, date_range: DateRange
    ) -> List[CodeQualityMetric]:
        """Récupère l'historique d'une métrique spécifique pour un projet."""
        pass
    
    @abstractmethod
    def save_metric(self, metric: CodeQualityMetric) -> CodeQualityMetric:
        """Persiste une métrique de qualité du code."""
        pass


class SecurityRepository(ABC):
    """Interface pour l'accès aux données de sécurité."""
    
    @abstractmethod
    def get_vulnerabilities(
        self, project_id: ProjectIdentifier, severity: Optional[str] = None
    ) -> List[SecurityVulnerability]:
        """Récupère les vulnérabilités pour un projet, avec filtrage optionnel par sévérité."""
        pass
    
    @abstractmethod
    def save_vulnerability(self, vulnerability: SecurityVulnerability) -> SecurityVulnerability:
        """Persiste une vulnérabilité de sécurité."""
        pass
    
    @abstractmethod
    def get_vulnerability_trend(
        self, project_id: ProjectIdentifier, date_range: DateRange
    ) -> Dict[datetime, int]:
        """Récupère la tendance des vulnérabilités sur une période donnée."""
        pass
