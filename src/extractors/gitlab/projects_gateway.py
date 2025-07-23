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
        """
        return self.client.extract_gitlab_resource(
            resource_type="projects",
            additional_parameters=params
        )

    def get_projects(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Récupère la liste des projets selon les critères fournis.
        """
        # Convertit None en dict vide pour la cohérence
        request_params = params if params is not None else {}
        return self.client.extract_gitlab_resource(
            resource_type="projects",
            additional_parameters=request_params
        )

    def get_project_members(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Récupère la liste des membres d'un projet.
        """
        return self.client.extract_gitlab_resource(
            resource_type=f"projects/{project_id}/members"
        )

    def get_project_commits(self, project_id: int, params: Optional[Dict[str, Any]] = None, since: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Récupère les commits d'un projet.
        """
        parameters = params.copy() if params else {}
        if since:
            parameters["since"] = since
        return self.client.extract_gitlab_resource(
            resource_type=f"projects/{project_id}/repository/commits",
            additional_parameters=parameters
        )

    def get_project_merge_requests(self, project_id: int, params: Optional[Dict[str, Any]] = None, updated_after: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Récupère les merge requests d'un projet.
        """
        parameters = params.copy() if params else {}
        if updated_after:
            parameters["updated_after"] = updated_after
        return self.client.extract_gitlab_resource(
            resource_type=f"projects/{project_id}/merge_requests",
            additional_parameters=parameters
        )

    def get_project_issues(self, project_id: int, params: Optional[Dict[str, Any]] = None, updated_after: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Récupère les issues d'un projet.
        """
        parameters = params.copy() if params else {}
        if updated_after:
            parameters["updated_after"] = updated_after
        return self.client.extract_gitlab_resource(
            resource_type=f"projects/{project_id}/issues",
            additional_parameters=parameters
        )

    def get_project_pipelines(self, project_id: int, params: Optional[Dict[str, Any]] = None, updated_after: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Récupère les pipelines d'un projet.
        """
        parameters = params.copy() if params else {}
        if updated_after:
            parameters["updated_after"] = updated_after
        return self.client.extract_gitlab_resource(
            resource_type=f"projects/{project_id}/pipelines",
            additional_parameters=parameters
        )

    def get_project_branches(self, project_id: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Récupère la liste des branches d'un projet.
        """
        return self.client.extract_gitlab_resource(
            resource_type=f"projects/{project_id}/repository/branches",
            additional_parameters=params
        )