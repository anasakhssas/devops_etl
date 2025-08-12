"""
Module contenant la passerelle pour l'accès aux projets GitLab.
"""
from typing import Any, Dict, List, Optional

from src.extractors.gitlab.gitlab_client_improved import GitLabClient


class GitLabProjectsGateway:
    """
    Passerelle pour accéder aux projets et leurs données associées dans GitLab.
    """

    def __init__(self, gitlab_client: GitLabClient):
        self.client = gitlab_client

    def get_projects(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Récupère la liste des projets selon les critères fournis.
        Exclut les projets archivés par défaut (archived=false).
        Pour inclure les projets archivés, passer params={"archived": True} ou "true".
        """
        request_params = params.copy() if params else {}
        if "archived" not in request_params:
            # Utilise la valeur "false" pour maximiser la compatibilité avec l'API GitLab
            request_params["archived"] = "false"
        return self.client.extract_gitlab_resource(
            resource_type="projects",
            additional_parameters=request_params
        )

    def get_project_members(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Récupère la liste des membres d'un projet.
        """
        return self.client.get_project_members(project_id)

    def get_project_commits(self, project_id: int, params: Optional[Dict[str, Any]] = None, since: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Récupère les commits d'un projet.
        """
        parameters = params.copy() if params else {}
        if since:
            parameters["since"] = since
        # Inclure les stats d'ajouts/suppressions pour chaque commit
        if "with_stats" not in parameters:
            parameters["with_stats"] = True
        return self.client.get_project_commits(project_id, parameters)

    def get_project_merge_requests(self, project_id: int, params: Optional[Dict[str, Any]] = None, updated_after: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Récupère les merge requests d'un projet.
        """
        parameters = params.copy() if params else {}
        if updated_after:
            parameters["updated_after"] = updated_after
        return self.client.get_project_merge_requests(project_id, parameters)

    def get_project_issues(self, project_id: int, params: Optional[Dict[str, Any]] = None, updated_after: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Récupère les issues d'un projet.
        """
        parameters = params.copy() if params else {}
        if updated_after:
            parameters["updated_after"] = updated_after
        return self.client.get_project_issues(project_id, parameters)

    def get_project_pipelines(self, project_id: int, params: Optional[Dict[str, Any]] = None, updated_after: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Récupère les pipelines d'un projet.
        """
        parameters = params.copy() if params else {}
        if updated_after:
            parameters["updated_after"] = updated_after
        return self.client.get_project_pipelines(project_id, parameters)

    def get_project_branches(self, project_id: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Récupère la liste des branches d'un projet.
        """
        return self.client.get_project_branches(project_id, params)

    def get_project_events(self, project_id: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Récupère les événements d'un projet.
        """
        parameters = params.copy() if params else {}
        # Maximiser le nombre d'items par page si la pagination n'est pas gérée en amont
        if "per_page" not in parameters:
            parameters["per_page"] = 100
        return self.client.get_project_events(project_id, parameters or {})