"""
Cas d'utilisation pour l'export de données GitLab.

Ce module contient les cas d'utilisation pour exporter différents types
de données depuis GitLab vers divers formats.
"""

import csv
import json
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union, cast
import pandas as pd

from src.domain.entities import Project, Developer, Commit
from src.domain.ports.repositories import ProjectRepository, DeveloperRepository, CommitRepository
from src.domain.services import ProjectAnalysisService
from src.domain.value_objects import DateRange


class BaseExportUseCase(ABC):
    """Classe de base pour les cas d'utilisation d'export."""
    
    @abstractmethod
    def execute(self, output_path: str, format: str = 'csv', **kwargs) -> str:
        """
        Exécute le cas d'utilisation d'export.
        
        Args:
            output_path: Chemin du fichier de sortie
            format: Format d'export ('csv', 'json', 'excel')
            **kwargs: Paramètres spécifiques au cas d'utilisation
            
        Returns:
            Chemin du fichier généré
        """
        pass
    
    def _ensure_directory_exists(self, output_path: str) -> None:
        """
        S'assure que le répertoire de sortie existe.
        
        Args:
            output_path: Chemin du fichier de sortie
        """
        directory = os.path.dirname(output_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
    
    def _export_data(self, data: List[Dict[str, Any]], output_path: str, format: str) -> str:
        """
        Exporte les données dans le format spécifié.
        
        Args:
            data: Données à exporter
            output_path: Chemin du fichier de sortie
            format: Format d'export ('csv', 'json', 'excel')
            
        Returns:
            Chemin du fichier généré
        """
        self._ensure_directory_exists(output_path)
        
        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        elif format == 'excel':
            df = pd.DataFrame(data)
            df.to_excel(output_path, index=False)
        else:  # csv par défaut
            if not data:
                # Créer un fichier CSV vide avec un en-tête par défaut
                with open(output_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['no_data'])
            else:
                # Utiliser les clés du premier élément comme en-tête
                fieldnames = list(data[0].keys())
                with open(output_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for row in data:
                        # Convertir tous les éléments en chaînes pour éviter les erreurs
                        sanitized_row = {
                            k: str(v) if isinstance(v, (datetime, dict, list)) else v 
                            for k, v in row.items()
                        }
                        writer.writerow(sanitized_row)
        
        return output_path


class ExportProjectsUseCase(BaseExportUseCase):
    """Cas d'utilisation pour exporter les projets."""
    
    def __init__(self, project_repository: ProjectRepository):
        """
        Initialise le cas d'utilisation.
        
        Args:
            project_repository: Repository pour accéder aux projets
        """
        self.project_repository = project_repository
    
    def execute(
        self, 
        output_path: str, 
        format: str = 'csv',
        include_archived: bool = False,
        only_active: bool = False,
        **kwargs
    ) -> str:
        """
        Exporte les projets dans un fichier.
        
        Args:
            output_path: Chemin du fichier de sortie
            format: Format d'export ('csv', 'json', 'excel')
            include_archived: Inclure les projets archivés
            only_active: N'inclure que les projets avec une activité récente
            **kwargs: Paramètres supplémentaires ignorés
            
        Returns:
            Chemin du fichier généré
        """
        try:
            # Récupérer tous les projets
            projects = self.project_repository.get_all()
            
            # Filtrer selon les paramètres
            if not include_archived:
                projects = [p for p in projects if not p.metadata.get('archived', False)]
                
            if only_active:
                # Définir "actif" comme ayant une activité dans les 30 derniers jours
                thirty_days_ago = datetime.now() - timedelta(days=30)
                projects = [
                    p for p in projects 
                    if p.last_activity_at and p.last_activity_at > thirty_days_ago
                ]
            
            # Préparer les données pour l'export
            export_data = []
            for project in projects:
                project_data = {
                    'id': str(project.id),
                    'name': project.name,
                    'description': project.description,
                    'url': project.url,
                    'created_at': project.created_at.isoformat() if project.created_at else None,
                    'last_activity_at': project.last_activity_at.isoformat() if project.last_activity_at else None,
                    'stars': project.stars_count,
                    'forks': project.forks_count,
                    'open_issues': project.open_issues_count,
                    'visibility': project.metadata.get('visibility', ''),
                    'default_branch': project.metadata.get('default_branch', ''),
                    'archived': project.metadata.get('archived', False),
                    'namespace': project.metadata.get('namespace', '')
                }
                export_data.append(project_data)
            
            # Exporter les données
            return self._export_data(export_data, output_path, format)
        except Exception as e:
            logging.error(f"Erreur lors de l'export des projets: {str(e)}")
            raise


class ExportDevelopersUseCase(BaseExportUseCase):
    """Cas d'utilisation pour exporter les développeurs."""
    
    def __init__(self, developer_repository: DeveloperRepository):
        """
        Initialise le cas d'utilisation.
        
        Args:
            developer_repository: Repository pour accéder aux développeurs
        """
        self.developer_repository = developer_repository
    
    def execute(
        self, 
        output_path: str, 
        format: str = 'csv',
        project_id: Optional[str] = None,
        identify_bots: bool = True,
        **kwargs
    ) -> str:
        """
        Exporte les développeurs dans un fichier.
        
        Args:
            output_path: Chemin du fichier de sortie
            format: Format d'export ('csv', 'json', 'excel')
            project_id: ID du projet pour filtrer les développeurs (optionnel)
            identify_bots: Identifier automatiquement les comptes de bot
            **kwargs: Paramètres supplémentaires ignorés
            
        Returns:
            Chemin du fichier généré
        """
        try:
            # Récupérer les développeurs selon le filtre
            if project_id:
                developers = self.developer_repository.get_by_project(project_id)
            else:
                developers = self.developer_repository.get_all()
            
            # Préparer les données pour l'export
            export_data = []
            for developer in developers:
                dev_data = {
                    'id': developer.id,
                    'name': developer.name,
                    'username': developer.username,
                    'email': developer.email,
                    'created_at': developer.created_at.isoformat() if developer.created_at else None,
                    'state': developer.metadata.get('state', ''),
                    'is_bot': developer.metadata.get('is_bot', False) if identify_bots else None,
                }
                
                # Ajouter des informations sur le rôle si filtre par projet
                if project_id:
                    dev_data['role'] = developer.metadata.get('role')
                    dev_data['role_name'] = developer.metadata.get('role_name')
                
                export_data.append(dev_data)
            
            # Exporter les données
            return self._export_data(export_data, output_path, format)
        except Exception as e:
            logging.error(f"Erreur lors de l'export des développeurs: {str(e)}")
            raise


class ExportCommitActivityUseCase(BaseExportUseCase):
    """Cas d'utilisation pour exporter l'activité des commits."""
    
    def __init__(self, commit_repository: CommitRepository):
        """
        Initialise le cas d'utilisation.
        
        Args:
            commit_repository: Repository pour accéder aux commits
        """
        self.commit_repository = commit_repository
    
    def execute(
        self, 
        output_path: str, 
        format: str = 'csv',
        project_id: str = None,
        days: int = 30,
        **kwargs
    ) -> str:
        """
        Exporte l'activité des commits dans un fichier.
        
        Args:
            output_path: Chemin du fichier de sortie
            format: Format d'export ('csv', 'json', 'excel')
            project_id: ID du projet (obligatoire)
            days: Nombre de jours à analyser
            **kwargs: Paramètres supplémentaires ignorés
            
        Returns:
            Chemin du fichier généré
            
        Raises:
            ValueError: Si project_id n'est pas fourni
        """
        if not project_id:
            raise ValueError("L'ID du projet est obligatoire pour l'export des commits")
        
        try:
            # Définir la plage de dates
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            date_range = DateRange(start_date=start_date, end_date=end_date)
            
            # Récupérer les statistiques des commits
            stats = self.commit_repository.get_commit_stats(project_id, date_range)
            
            # Récupérer les commits détaillés
            commits = self.commit_repository.get_by_project(project_id, date_range)
            
            # Préparer les données pour l'export - commencer par les statistiques globales
            export_data = [{
                'project_id': str(project_id),
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_commits': stats.get('total_commits', 0),
                'unique_authors': stats.get('unique_authors', 0),
                'additions': stats.get('additions', 0),
                'deletions': stats.get('deletions', 0),
                'net_changes': stats.get('net_changes', 0),
                'commits_per_day': stats.get('commits_per_day', 0),
                'report_type': 'summary'
            }]
            
            # Ajouter les détails de chaque commit
            for commit in commits:
                commit_data = {
                    'project_id': str(project_id),
                    'commit_id': commit.id,
                    'author_name': commit.author_name,
                    'author_email': commit.author_email,
                    'date': commit.date.isoformat(),
                    'message': commit.message,
                    'additions': commit.stats.get('additions', 0),
                    'deletions': commit.stats.get('deletions', 0),
                    'files_changed': len(commit.files),
                    'report_type': 'detail'
                }
                export_data.append(commit_data)
            
            # Exporter les données
            return self._export_data(export_data, output_path, format)
        except Exception as e:
            logging.error(f"Erreur lors de l'export de l'activité des commits: {str(e)}")
            raise


class ExportProjectHealthUseCase(BaseExportUseCase):
    """Cas d'utilisation pour exporter les indicateurs de santé d'un projet."""
    
    def __init__(self, project_analysis_service: ProjectAnalysisService):
        """
        Initialise le cas d'utilisation.
        
        Args:
            project_analysis_service: Service d'analyse de projet
        """
        self.project_analysis_service = project_analysis_service
    
    def execute(
        self, 
        output_path: str, 
        format: str = 'csv',
        project_ids: List[str] = None,
        **kwargs
    ) -> str:
        """
        Exporte les indicateurs de santé d'un ou plusieurs projets.
        
        Args:
            output_path: Chemin du fichier de sortie
            format: Format d'export ('csv', 'json', 'excel')
            project_ids: Liste des IDs de projets à analyser
            **kwargs: Paramètres supplémentaires ignorés
            
        Returns:
            Chemin du fichier généré
            
        Raises:
            ValueError: Si aucun project_id n'est fourni
        """
        if not project_ids:
            raise ValueError("Au moins un ID de projet est nécessaire pour l'analyse de santé")
        
        try:
            # Analyser chaque projet
            export_data = []
            for project_id in project_ids:
                # Obtenir le rapport de santé
                health_report = self.project_analysis_service.analyze_project_health(project_id)
                
                # Extraire les métriques principales pour l'export
                project_data = {
                    'project_id': str(project_id),
                    'project_name': health_report.get('project_name', 'Unknown'),
                    'analysis_date': datetime.now().isoformat(),
                    'health_score': health_report.get('health_score', 0),
                    'commit_frequency': health_report.get('metrics', {}).get('commit_activity', {}).get('frequency', 0),
                    'unique_contributors': health_report.get('metrics', {}).get('commit_activity', {}).get('unique_contributors', 0),
                    'code_coverage': health_report.get('metrics', {}).get('code_quality', {}).get('code_coverage', 0),
                    'technical_debt': health_report.get('metrics', {}).get('code_quality', {}).get('technical_debt', 0),
                    'total_vulnerabilities': health_report.get('metrics', {}).get('security', {}).get('total_vulnerabilities', 0),
                    'high_severity_vulnerabilities': health_report.get('metrics', {}).get('security', {}).get('high_severity', 0),
                }
                export_data.append(project_data)
            
            # Exporter les données
            return self._export_data(export_data, output_path, format)
        except Exception as e:
            logging.error(f"Erreur lors de l'export des indicateurs de santé: {str(e)}")
            raise
