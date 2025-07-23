"""
Module contenant la passerelle pour l'accès aux projets GitLab.
"""
from typing import Any, Dict, List, Optional

from src.extractors.gitlab.gitlab_client_improved import GitLabClient


class GitLabProjectsGateway:
    """
    Passerelle pour accéder aux projets et leurs données associées dans GitLab.
    Cette classe est spécialisée dans la récupération des données relatives aux projets.
    """

    def __init__(self, gitlab_client: GitLabClient):
        """
        Initialise la passerelle avec un client GitLab.
        
        Args:
            gitlab_client: Instance du client GitLab pour effectuer les requêtes API.
        """
        self.client = gitlab_client

    def get_projects(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Récupère la liste des projets selon les critères fournis.
        
        Args:
            params: Dictionnaire de paramètres pour filtrer les projets.
                   Exemples: 
                   - membership=True (projets où l'utilisateur est membre)
                   - owned=True (projets possédés par l'utilisateur)
                   - search="nom" (recherche par nom)
                   - min_access_level=30 (niveau d'accès minimum)
        
        Returns:
            Liste de dictionnaires représentant les projets.
        """
        return self.client.extract(resource="projects", params=params)

    def get_project(self, project_id: int) -> Dict[str, Any]:
        """
        Récupère les détails d'un projet spécifique.
        
        Args:
            project_id: Identifiant du projet à récupérer.
            
        Returns:
            Dictionnaire représentant les détails du projet.
        """
        results = self.client.extract(resource="projects", resource_id=project_id)
        return results[0] if results else {}

    def get_project_members(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Récupère la liste des membres d'un projet.
        
        Args:
            project_id: Identifiant du projet.
            
        Returns:
            Liste de dictionnaires représentant les membres du projet.
        """
        return self.client.extract(
            resource=f"projects/{project_id}/members/all"
        )

    def get_project_commits(self, project_id: int, params: Optional[Dict[str, Any]] = None, since: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Récupère les commits d'un projet, extraction incrémentale possible.
        
        Args:
            project_id: Identifiant du projet.
            params: Paramètres de filtrage comme:
                   - ref_name="branch" (branche spécifique)
                   - since="YYYY-MM-DD" (commits depuis date)
                   - until="YYYY-MM-DD" (commits jusqu'à date)
            since: Date de début au format "YYYY-MM-DD" (extraction incrémentale)
        Returns:
            Liste de dictionnaires représentant les commits.
        """
        parameters = params.copy() if params else {}
        if since:
            parameters["since"] = since
        return self.client.extract(
            resource=f"projects/{project_id}/repository/commits",
            params=parameters
        )

    def get_project_merge_requests(self, project_id: int, params: Optional[Dict[str, Any]] = None, updated_after: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Récupère les merge requests d'un projet, extraction incrémentale possible.
        
        Args:
            project_id: Identifiant du projet.
            params: Paramètres de filtrage comme:
                   - state="opened" (état: opened, closed, locked, merged)
                   - created_after="YYYY-MM-DD" (créées après date)
                   - updated_after="YYYY-MM-DD" (mises à jour après date)
            updated_after: Date de mise à jour au format "YYYY-MM-DD" (extraction incrémentale)
        Returns:
            Liste de dictionnaires représentant les merge requests.
        """
        parameters = params.copy() if params else {}
        if updated_after:
            parameters["updated_after"] = updated_after
        return self.client.extract(
            resource=f"projects/{project_id}/merge_requests",
            params=parameters
        )

    def get_project_issues(self, project_id: int, params: Optional[Dict[str, Any]] = None, updated_after: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Récupère les issues d'un projet, extraction incrémentale possible.
        
        Args:
            project_id: Identifiant du projet.
            params: Paramètres de filtrage comme:
                   - state="opened" (état: opened, closed)
                   - labels="bug,critical" (filtrage par labels)
                   - created_after="YYYY-MM-DD" (créées après date)
            updated_after: Date de mise à jour au format "YYYY-MM-DD" (extraction incrémentale)
        Returns:
            Liste de dictionnaires représentant les issues.
        """
        parameters = params.copy() if params else {}
        if updated_after:
            parameters["updated_after"] = updated_after
        return self.client.extract(
            resource=f"projects/{project_id}/issues",
            params=parameters
        )

    def get_project_pipelines(self, project_id: int, params: Optional[Dict[str, Any]] = None, updated_after: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Récupère les pipelines d'un projet, extraction incrémentale possible.
        
        Args:
            project_id: Identifiant du projet.
            params: Paramètres de filtrage comme:
                   - status="success" (statut: running, pending, success, failed, canceled)
                   - ref="main" (référence/branche)
                   - updated_after="YYYY-MM-DD" (mises à jour après date)
            updated_after: Date de mise à jour au format "YYYY-MM-DD" (extraction incrémentale)
        Returns:
            Liste de dictionnaires représentant les pipelines.
        """
        parameters = params.copy() if params else {}
        if updated_after:
            parameters["updated_after"] = updated_after
        return self.client.extract(
            resource=f"projects/{project_id}/pipelines",
            params=parameters
        )
        
    #extraction des branches 
    def get_project_branches(self, project_id: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
      """
     Récupère la liste des branches d’un projet GitLab.
    
    Args:
        project_id: Identifiant du projet.
        params: Paramètres supplémentaires (optionnel).
    
    Returns:
        Liste de dictionnaires représentant les branches.
    """
      return self.client.extract(
        resource=f"projects/{project_id}/repository/branches",
        params=params or {}
    )
 