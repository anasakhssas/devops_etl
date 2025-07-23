"""
Interfaces de repository pour le domaine DevOps ETL.

Ce module définit les interfaces (ports) que doivent implémenter les adaptateurs
pour accéder aux données des différentes sources.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any, Set

from src.domain.entities import Project, Developer, CodeQualityMetric, Commit, SecurityVulnerability
from src.domain.value_objects import DateRange, CommitActivity


class ProjectRepository(ABC):
    """
    Interface pour l'accès aux données des projets.
    """
    
    @abstractmethod
    def get_all(self) -> List[Project]:
        """
        Récupère tous les projets.
        
        Returns:
            Liste des projets.
        """
        pass
    
    @abstractmethod
    def get_by_id(self, project_id: str) -> Optional[Project]:
        """
        Récupère un projet par son ID.
        
        Args:
            project_id: ID du projet à récupérer.
            
        Returns:
            Le projet correspondant ou None s'il n'existe pas.
        """
        pass
    
    @abstractmethod
    def save(self, project: Project) -> Project:
        """
        Sauvegarde un projet (création ou mise à jour).
        
        Args:
            project: Le projet à sauvegarder.
            
        Returns:
            Le projet sauvegardé, potentiellement avec des champs mis à jour.
        """
        pass


class DeveloperRepository(ABC):
    """
    Interface pour l'accès aux données des développeurs.
    """
    
    @abstractmethod
    def get_all(self) -> List[Developer]:
        """
        Récupère tous les développeurs.
        
        Returns:
            Liste des développeurs.
        """
        pass
    
    @abstractmethod
    def get_by_id(self, developer_id: str) -> Optional[Developer]:
        """
        Récupère un développeur par son ID.
        
        Args:
            developer_id: ID du développeur à récupérer.
            
        Returns:
            Le développeur correspondant ou None s'il n'existe pas.
        """
        pass
    
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[Developer]:
        """
        Récupère un développeur par son nom d'utilisateur.
        
        Args:
            username: Nom d'utilisateur du développeur à récupérer.
            
        Returns:
            Le développeur correspondant ou None s'il n'existe pas.
        """
        pass
    
    @abstractmethod
    def get_by_project(self, project_id: str) -> List[Developer]:
        """
        Récupère tous les développeurs associés à un projet.
        
        Args:
            project_id: ID du projet.
            
        Returns:
            Liste des développeurs associés au projet.
        """
        pass


class CommitRepository(ABC):
    """
    Interface pour l'accès aux données des commits.
    """
    
    @abstractmethod
    def get_by_project(self, project_id: str) -> List[Commit]:
        """
        Récupère tous les commits d'un projet.
        
        Args:
            project_id: ID du projet.
            
        Returns:
            Liste des commits du projet.
        """
        pass
    
    @abstractmethod
    def get_by_author(self, author_id: str) -> List[Commit]:
        """
        Récupère tous les commits d'un auteur.
        
        Args:
            author_id: ID de l'auteur.
            
        Returns:
            Liste des commits de l'auteur.
        """
        pass
    
    @abstractmethod
    def get_activity(self, project_id: str, date_range: DateRange) -> CommitActivity:
        """
        Récupère l'activité des commits d'un projet sur une période donnée.
        
        Args:
            project_id: ID du projet.
            date_range: Période d'analyse.
            
        Returns:
            Objet CommitActivity représentant l'activité des commits.
        """
        pass


class CodeQualityRepository(ABC):
    """
    Interface pour l'accès aux données de qualité de code.
    """
    
    @abstractmethod
    def get_metrics(self, project_id: str) -> List[CodeQualityMetric]:
        """
        Récupère toutes les métriques de qualité pour un projet.
        
        Args:
            project_id: ID du projet.
            
        Returns:
            Liste des métriques de qualité du projet.
        """
        pass
    
    @abstractmethod
    def get_metrics_by_type(self, project_id: str, metric_type: str) -> List[CodeQualityMetric]:
        """
        Récupère les métriques d'un type spécifique pour un projet.
        
        Args:
            project_id: ID du projet.
            metric_type: Type de métrique.
            
        Returns:
            Liste des métriques du type spécifié.
        """
        pass
    
    @abstractmethod
    def save_metric(self, metric: CodeQualityMetric) -> CodeQualityMetric:
        """
        Sauvegarde une métrique de qualité de code.
        
        Args:
            metric: La métrique à sauvegarder.
            
        Returns:
            La métrique sauvegardée.
        """
        pass


class SecurityRepository(ABC):
    """
    Interface pour l'accès aux données de sécurité.
    """
    
    @abstractmethod
    def get_vulnerabilities(self, project_id: str) -> List[SecurityVulnerability]:
        """
        Récupère toutes les vulnérabilités pour un projet.
        
        Args:
            project_id: ID du projet.
            
        Returns:
            Liste des vulnérabilités du projet.
        """
        pass
    
    @abstractmethod
    def get_by_severity(self, project_id: str, severity: str) -> List[SecurityVulnerability]:
        """
        Récupère les vulnérabilités d'un niveau de gravité spécifique.
        
        Args:
            project_id: ID du projet.
            severity: Niveau de gravité ("info", "low", "medium", "high", "critical").
            
        Returns:
            Liste des vulnérabilités du niveau spécifié.
        """
        pass
