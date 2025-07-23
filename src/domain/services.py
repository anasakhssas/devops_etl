"""
Services du domaine DevOps ETL.

Ce module contient les services qui encapsulent la logique métier
complexe qui ne peut pas être attribuée à une seule entité.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set, Tuple

from src.domain.entities import Project, Developer, CodeQualityMetric, SecurityVulnerability
from src.domain.value_objects import DateRange, CommitActivity, TechnicalDebt, CodeCoverage
from src.domain.ports.repositories import (
    ProjectRepository, 
    DeveloperRepository, 
    CommitRepository, 
    CodeQualityRepository,
    SecurityRepository
)


class ProjectAnalysisService:
    """
    Service pour analyser les métriques d'un projet.
    """
    
    def __init__(
        self,
        commit_repository: CommitRepository,
        code_quality_repository: CodeQualityRepository,
        security_repository: SecurityRepository
    ):
        """
        Initialise le service d'analyse de projet.
        
        Args:
            commit_repository: Repository pour accéder aux commits
            code_quality_repository: Repository pour accéder aux métriques de qualité
            security_repository: Repository pour accéder aux vulnérabilités
        """
        self.commit_repository = commit_repository
        self.code_quality_repository = code_quality_repository
        self.security_repository = security_repository
    
    def calculate_productivity_metrics(self, project_id: str, date_range: DateRange) -> Dict[str, Any]:
        """
        Calcule les métriques de productivité pour un projet sur une période donnée.
        
        Args:
            project_id: ID du projet à analyser
            date_range: Période d'analyse
            
        Returns:
            Dictionnaire contenant les métriques de productivité
        """
        # Récupération des données nécessaires
        commit_activity = self.commit_repository.get_activity(project_id, date_range)
        
        # Calcul des métriques
        duration_days = date_range.duration.days or 1  # Éviter division par zéro
        
        metrics = {
            "commit_count": commit_activity.count,
            "commit_frequency": commit_activity.count / duration_days,
            "active_developer_count": commit_activity.author_count,
            "code_churn": commit_activity.total_changes,
            "net_code_growth": commit_activity.net_changes,
            "period_days": duration_days
        }
        
        return metrics
    
    def calculate_quality_metrics(self, project_id: str) -> Dict[str, Any]:
        """
        Calcule les métriques de qualité actuelles pour un projet.
        
        Args:
            project_id: ID du projet à analyser
            
        Returns:
            Dictionnaire contenant les métriques de qualité
        """
        # Récupération des métriques de qualité
        quality_metrics = self.code_quality_repository.get_metrics(project_id)
        
        # Organisation des métriques par type
        metrics_by_type = {}
        for metric in quality_metrics:
            if metric.metric_type not in metrics_by_type:
                metrics_by_type[metric.metric_type] = []
            metrics_by_type[metric.metric_type].append(metric)
        
        # Extraction des dernières valeurs pour chaque type
        latest_metrics = {}
        for metric_type, metrics in metrics_by_type.items():
            # Tri par timestamp décroissant
            sorted_metrics = sorted(metrics, key=lambda m: m.timestamp, reverse=True)
            if sorted_metrics:
                latest_metrics[metric_type] = sorted_metrics[0].value
        
        return latest_metrics
    
    def calculate_security_posture(self, project_id: str) -> Dict[str, Any]:
        """
        Calcule la posture de sécurité actuelle pour un projet.
        
        Args:
            project_id: ID du projet à analyser
            
        Returns:
            Dictionnaire contenant les métriques de sécurité
        """
        # Récupération des vulnérabilités
        vulnerabilities = self.security_repository.get_vulnerabilities(project_id)
        
        # Comptage par niveau de gravité
        severity_counts = {severity: 0 for severity in SecurityVulnerability.SEVERITY_LEVELS}
        for vulnerability in vulnerabilities:
            if vulnerability.status != "fixed":
                severity_counts[vulnerability.severity] += 1
        
        # Calcul d'un score de risque pondéré
        weights = {
            "info": 0.1,
            "low": 1,
            "medium": 3,
            "high": 5,
            "critical": 10
        }
        
        risk_score = sum(
            severity_counts[severity] * weights[severity]
            for severity in SecurityVulnerability.SEVERITY_LEVELS
        )
        
        return {
            "vulnerability_counts": severity_counts,
            "total_vulnerabilities": sum(severity_counts.values()),
            "risk_score": risk_score,
        }


class TeamAnalysisService:
    """
    Service pour analyser les métriques d'équipe et de développeurs.
    """
    
    def __init__(
        self,
        developer_repository: DeveloperRepository,
        commit_repository: CommitRepository
    ):
        """
        Initialise le service d'analyse d'équipe.
        
        Args:
            developer_repository: Repository pour accéder aux développeurs
            commit_repository: Repository pour accéder aux commits
        """
        self.developer_repository = developer_repository
        self.commit_repository = commit_repository
    
    def calculate_team_metrics(self, project_id: str, date_range: DateRange) -> Dict[str, Any]:
        """
        Calcule les métriques d'équipe pour un projet sur une période donnée.
        
        Args:
            project_id: ID du projet à analyser
            date_range: Période d'analyse
            
        Returns:
            Dictionnaire contenant les métriques d'équipe
        """
        # Récupération des données nécessaires
        developers = self.developer_repository.get_by_project(project_id)
        commit_activity = self.commit_repository.get_activity(project_id, date_range)
        
        # Calcul des métriques
        metrics = {
            "team_size": len(developers),
            "active_developers": commit_activity.author_count,
            "participation_rate": commit_activity.author_count / len(developers) if developers else 0,
        }
        
        return metrics
    
    def calculate_developer_metrics(
        self, 
        developer_id: str, 
        date_range: DateRange
    ) -> Dict[str, Any]:
        """
        Calcule les métriques individuelles pour un développeur sur une période donnée.
        
        Args:
            developer_id: ID du développeur à analyser
            date_range: Période d'analyse
            
        Returns:
            Dictionnaire contenant les métriques du développeur
        """
        # Récupération des commits du développeur
        commits = self.commit_repository.get_by_author(developer_id)
        
        # Filtrer les commits dans la période
        period_commits = [
            commit for commit in commits 
            if date_range.start_date <= commit.timestamp <= date_range.end_date
        ]
        
        # Regrouper les commits par projet
        commits_by_project = {}
        for commit in period_commits:
            if commit.project_id not in commits_by_project:
                commits_by_project[commit.project_id] = []
            commits_by_project[commit.project_id].append(commit)
        
        # Calcul des métriques
        metrics = {
            "commit_count": len(period_commits),
            "projects_contributed": len(commits_by_project),
            "additions": sum(c.stats["additions"] for c in period_commits),
            "deletions": sum(c.stats["deletions"] for c in period_commits),
            "total_changes": sum(c.stats["changes"] for c in period_commits),
        }
        
        return metrics
