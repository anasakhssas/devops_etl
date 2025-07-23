"""
Implémentation GitLab du repository de projets.

Ce module contient l'adaptateur GitLab qui implémente l'interface ProjectRepository
du domaine pour accéder aux données des projets depuis GitLab.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, cast

# Correction de l'importation pour utiliser le bon chemin
from src.domain.entities import Project
from src.domain.repositories import ProjectRepository 
from src.domain.value_objects import ProjectIdentifier
from src.adapters.gitlab.gitlab_client import GitLabClient


class GitLabProjectRepository(ProjectRepository):
    """
    Implémentation du repository de projets utilisant l'API GitLab.
    """
    
    def __init__(self, gitlab_client: GitLabClient):
        """
        Initialise le repository avec un client GitLab.
        
        Args:
            gitlab_client: Client GitLab configuré
        """
        self.client = gitlab_client
    
    def get_all(self) -> List[Project]:
        """
        Récupère tous les projets accessibles via l'API GitLab.
        
        Returns:
            Liste des projets
        """
        try:
            # Récupération des projets depuis l'API
            gitlab_projects = self.client.get_projects()
            
            # Conversion en entités du domaine
            return [self._to_domain_entity(project_data) for project_data in gitlab_projects]
        except Exception as e:
            logging.error(f"Erreur lors de la récupération de tous les projets: {str(e)}")
            raise
    
    def get_by_id(self, project_id: str) -> Optional[Project]:
        """
        Récupère un projet par son ID.
        
        Args:
            project_id: ID ou chemin du projet (namespace/project)
            
        Returns:
            Le projet correspondant ou None s'il n'existe pas
        """
        try:
            project_data = self.client.get_project(project_id)
            return self._to_domain_entity(project_data)
        except ValueError:
            # Projet non trouvé
            return None
        except Exception as e:
            logging.error(f"Erreur lors de la récupération du projet {project_id}: {str(e)}")
            raise
    
    def save(self, project: Project) -> Project:
        """
        Sauvegarde un projet (non implémenté car l'API GitLab ne permet généralement
        pas la création ou modification de projets via des tokens standard).
        
        Args:
            project: Le projet à sauvegarder
            
        Returns:
            Le projet sauvegardé
            
        Raises:
            NotImplementedError: Cette méthode n'est pas implémentée
        """
        # Note: La création/modification de projets nécessite des permissions spéciales
        # et n'est généralement pas utilisée dans un contexte ETL
        raise NotImplementedError("La sauvegarde de projets n'est pas implémentée via l'API GitLab")
    
    def get_projects_by_criteria(self, criteria: Dict[str, Any]) -> List[Project]:
        """
        Récupère les projets selon des critères spécifiques.
        
        Args:
            criteria: Dictionnaire de critères de filtrage
            
        Returns:
            Liste des projets correspondant aux critères
        """
        try:
            # Conversion des critères pour l'API GitLab
            gitlab_params = {}
            
            # Traiter les critères spécifiques pour les adapter à l'API GitLab
            if 'name' in criteria:
                gitlab_params['search'] = criteria['name']
            
            if 'visibility' in criteria:
                gitlab_params['visibility'] = criteria['visibility']
                
            if 'archived' in criteria:
                gitlab_params['archived'] = criteria['archived']
            
            if 'membership' in criteria:
                gitlab_params['membership'] = criteria['membership']
            
            # Appliquer d'autres critères directement
            for key, value in criteria.items():
                if key not in ['name', 'visibility', 'archived', 'membership']:
                    gitlab_params[key] = value
            
            # Récupération des projets depuis l'API
            gitlab_projects = self.client.get_projects(**gitlab_params)
            
            # Conversion en entités du domaine
            return [self._to_domain_entity(project_data) for project_data in gitlab_projects]
        except Exception as e:
            logging.error(f"Erreur lors de la recherche de projets: {str(e)}")
            raise
    
    def _to_domain_entity(self, project_data: Dict[str, Any]) -> Project:
        """
        Convertit les données GitLab en entité du domaine Project.
        
        Args:
            project_data: Données du projet provenant de l'API GitLab
            
        Returns:
            Entité Project correspondante
        """
        # Extraction des données pertinentes
        project_id = ProjectIdentifier(str(project_data['id']))
        name = project_data['name']
        description = project_data.get('description', '')
        url = project_data.get('web_url', '')
        
        # Dates de création et dernière activité
        created_at = None
        if 'created_at' in project_data:
            try:
                created_at = datetime.fromisoformat(project_data['created_at'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass
        
        last_activity_at = None
        if 'last_activity_at' in project_data:
            try:
                last_activity_at = datetime.fromisoformat(project_data['last_activity_at'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass
        
        # Récupération des métriques
        stars_count = project_data.get('star_count', 0)
        forks_count = project_data.get('forks_count', 0)
        open_issues_count = project_data.get('open_issues_count', 0)
        
        # Informations supplémentaires
        metadata = {
            'visibility': project_data.get('visibility', ''),
            'default_branch': project_data.get('default_branch', ''),
            'archived': project_data.get('archived', False),
            'namespace': project_data.get('namespace', {}).get('path', '') if project_data.get('namespace') else '',
            'repository_access_level': project_data.get('repository_access_level', ''),
            'merge_requests_access_level': project_data.get('merge_requests_access_level', ''),
            'issues_access_level': project_data.get('issues_access_level', ''),
        }
        
        # Création de l'entité Project
        return Project(
            id=project_id,
            name=name,
            description=description,
            url=url,
            created_at=created_at,
            last_activity_at=last_activity_at,
            stars_count=stars_count,
            forks_count=forks_count,
            open_issues_count=open_issues_count,
            metadata=metadata
        )
