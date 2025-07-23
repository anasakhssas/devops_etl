"""
Implémentation GitLab du repository de commits.

Ce module contient l'adaptateur GitLab qui implémente l'interface CommitRepository
du domaine pour accéder aux données des commits depuis GitLab.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, cast

from src.domain.entities import Commit
from src.domain.ports.repositories import CommitRepository
from src.domain.value_objects import DateRange, CommitActivity, ProjectIdentifier
from src.adapters.gitlab.gitlab_client import GitLabClient


class GitLabCommitRepository(CommitRepository):
    """
    Implémentation du repository de commits utilisant l'API GitLab.
    """
    
    def __init__(self, gitlab_client: GitLabClient):
        """
        Initialise le repository avec un client GitLab.
        
        Args:
            gitlab_client: Client GitLab configuré
        """
        self.client = gitlab_client
    
    def get_by_project(self, project_id: ProjectIdentifier, date_range: Optional[DateRange] = None) -> List[Commit]:
        """
        Récupère les commits d'un projet, optionnellement filtrés par date.
        
        Args:
            project_id: Identifiant du projet
            date_range: Plage de dates pour filtrer les commits
            
        Returns:
            Liste des commits du projet
        """
        try:
            # Préparer les paramètres de date
            since = None
            until = None
            if date_range:
                since = date_range.start_date.isoformat() if date_range.start_date else None
                until = date_range.end_date.isoformat() if date_range.end_date else None
            
            # Récupérer les commits depuis l'API GitLab
            commits_data = self.client.get_commits(str(project_id), since, until)
            
            # Convertir en entités du domaine
            return [self._to_domain_entity(commit_data, project_id) for commit_data in commits_data]
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des commits du projet {project_id}: {str(e)}")
            raise
    
    def get_by_developer(self, developer_id: str, date_range: Optional[DateRange] = None) -> List[Commit]:
        """
        Récupère les commits d'un développeur, optionnellement filtrés par date.
        
        Note: Cette implémentation est inefficace car elle doit interroger chaque projet.
        Une implémentation plus efficace nécessiterait des API spécifiques ou une base de données locale.
        
        Args:
            developer_id: ID du développeur
            date_range: Plage de dates pour filtrer les commits
            
        Returns:
            Liste des commits du développeur
            
        Raises:
            NotImplementedError: Cette méthode n'est pas implémentée efficacement
        """
        # Cette méthode nécessiterait une base de données locale ou un accès à tous les projets,
        # ce qui n'est pas efficace avec l'API GitLab standard
        raise NotImplementedError(
            "La récupération des commits par développeur n'est pas implémentée efficacement "
            "avec l'API GitLab. Utilisez un cache local ou une base de données."
        )
    
    def save(self, commit: Commit) -> Commit:
        """
        Persiste un commit (non implémentée car l'API GitLab ne permet pas
        la création directe de commits via l'API).
        
        Args:
            commit: Le commit à persister
            
        Returns:
            Le commit persisté
            
        Raises:
            NotImplementedError: Cette méthode n'est pas implémentée
        """
        raise NotImplementedError("La sauvegarde de commits n'est pas possible via l'API GitLab")
    
    def get_commit_stats(self, project_id: ProjectIdentifier, date_range: DateRange) -> Dict[str, Any]:
        """
        Récupère des statistiques sur les commits d'un projet pour une période donnée.
        
        Args:
            project_id: Identifiant du projet
            date_range: Plage de dates pour l'analyse
            
        Returns:
            Dictionnaire contenant les statistiques des commits
        """
        try:
            # Préparer les paramètres de date
            since = date_range.start_date.isoformat() if date_range.start_date else None
            until = date_range.end_date.isoformat() if date_range.end_date else None
            
            # Récupérer les statistiques depuis l'API GitLab
            stats = self.client.get_commit_stats(str(project_id), since, until)
            
            # Créer un dictionnaire de résultats enrichi
            result = {
                "total_commits": stats["total_commits"],
                "unique_authors": stats["unique_authors"],
                "authors": stats["authors"],
                "additions": stats["total_additions"],
                "deletions": stats["total_deletions"],
                "net_changes": stats["net_changes"],
                "date_range": {
                    "start": date_range.start_date.isoformat() if date_range.start_date else None,
                    "end": date_range.end_date.isoformat() if date_range.end_date else None,
                    "days": date_range.duration.days if date_range.duration else None
                },
                "project_id": str(project_id)
            }
            
            # Calculer des métriques supplémentaires si possible
            if date_range.duration and date_range.duration.days > 0:
                result["commits_per_day"] = stats["total_commits"] / date_range.duration.days
            else:
                result["commits_per_day"] = stats["total_commits"]  # En cas de plage d'un jour
            
            if stats["unique_authors"] > 0:
                result["commits_per_author"] = stats["total_commits"] / stats["unique_authors"]
            else:
                result["commits_per_author"] = 0
                
            return result
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des statistiques de commits pour le projet {project_id}: {str(e)}")
            raise
    
    def get_activity(self, project_id: ProjectIdentifier, date_range: DateRange) -> CommitActivity:
        """
        Récupère l'activité de commits d'un projet pour une période donnée.
        
        Args:
            project_id: Identifiant du projet
            date_range: Plage de dates pour l'analyse
            
        Returns:
            Objet CommitActivity contenant les statistiques d'activité
        """
        stats = self.get_commit_stats(project_id, date_range)
        
        # Créer un objet CommitActivity à partir des statistiques
        return CommitActivity(
            count=stats["total_commits"],
            author_count=stats["unique_authors"],
            total_changes=stats["additions"] + stats["deletions"],
            net_changes=stats["net_changes"],
            period=date_range
        )
    
    def _to_domain_entity(self, commit_data: Dict[str, Any], project_id: ProjectIdentifier) -> Commit:
        """
        Convertit les données GitLab en entité du domaine Commit.
        
        Args:
            commit_data: Données du commit provenant de l'API GitLab
            project_id: Identifiant du projet associé
            
        Returns:
            Entité Commit correspondante
        """
        # Extraction des données pertinentes
        commit_id = commit_data.get('id', '')
        message = commit_data.get('message', '')
        author_name = commit_data.get('author_name', '')
        author_email = commit_data.get('author_email', '')
        
        # Date du commit
        commit_date = None
        if 'created_at' in commit_data:
            try:
                commit_date = datetime.fromisoformat(commit_data['created_at'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass
        elif 'committed_date' in commit_data:
            try:
                commit_date = datetime.fromisoformat(commit_data['committed_date'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass
        
        # Statistiques du commit
        stats = {
            'additions': commit_data.get('stats', {}).get('additions', 0),
            'deletions': commit_data.get('stats', {}).get('deletions', 0),
            'total': commit_data.get('stats', {}).get('total', 0)
        }
        
        # Liste des fichiers modifiés
        files = []
        if 'files' in commit_data:
            files = [file_data.get('filename', '') for file_data in commit_data['files']]
        
        # Métadonnées additionnelles
        metadata = {
            'web_url': commit_data.get('web_url', ''),
            'parent_ids': commit_data.get('parent_ids', []),
            'title': commit_data.get('title', '')
        }
        
        # Création de l'entité Commit
        return Commit(
            id=commit_id,
            project_id=str(project_id),
            message=message,
            author_name=author_name,
            author_email=author_email,
            date=commit_date or datetime.now(),  # Fallback à la date actuelle si non disponible
            stats=stats,
            files=files,
            metadata=metadata
        )
