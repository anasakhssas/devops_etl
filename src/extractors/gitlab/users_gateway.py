"""
Module contenant la passerelle pour l'accès aux utilisateurs GitLab.
"""
from typing import Any, Dict, List, Optional

from src.extractors.gitlab.gitlab_client_improved import GitLabClient


class GitLabUsersGateway:
    """
    Passerelle pour accéder aux membres d'un groupe GitLab.
    """

    def __init__(self, gitlab_client: GitLabClient):
        self.client = gitlab_client

    def get_group_members(self, group_id: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Récupère les membres d'un groupe GitLab.

        Args:
            group_id: Identifiant du groupe.
            params: Paramètres de filtrage optionnels.

        Returns:
            Liste de dictionnaires représentant les membres du groupe.
        """
        try:
            if not self.client.is_connected:
                self.client.connect()
            endpoint = f"/groups/{group_id}/members/all"
            # Utilisez la méthode http_get de l'objet _gitlab_client
            response = self.client._gitlab_client.http_get(endpoint, params=params or {})
            return response if isinstance(response, list) else []
        except Exception as e:
            self.client._logger.error(f"Erreur lors de la récupération des membres du groupe {group_id}: {e}")
            return []

    def get_all_users(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Récupère tous les utilisateurs internes de l'instance GitLab (pagination gérée).

        Args:
            params: Paramètres de filtrage optionnels.

        Returns:
            Liste de dictionnaires représentant les utilisateurs internes.
        """
        try:
            if not self.client.is_connected:
                self.client.connect()
            params = params.copy() if params else {}
            params["external"] = False
            params["per_page"] = 100
            endpoint = "/users"
            all_users = []
            page = 1
            while True:
                params["page"] = page
                response = self.client._gitlab_client.http_get(endpoint, params=params)
                if not response or not isinstance(response, list):
                    break
                all_users.extend(response)
                if len(response) < params["per_page"]:
                    break
                page += 1
            return all_users
        except Exception as e:
            self.client._logger.error(f"Erreur lors de la récupération des utilisateurs: {e}")
            return []

    def get_all_groups(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Récupère tous les groupes de l'instance GitLab (pagination gérée).

        Args:
            params: Paramètres de filtrage optionnels.

        Returns:
            Liste de dictionnaires représentant les groupes.
        """
        try:
            if not self.client.is_connected:
                self.client.connect()
            params = params.copy() if params else {}
            params["per_page"] = 100
            endpoint = "/groups"
            all_groups = []
            page = 1
            while True:
                params["page"] = page
                response = self.client._gitlab_client.http_get(endpoint, params=params)
                if not response or not isinstance(response, list):
                    break
                all_groups.extend(response)
                if len(response) < params["per_page"]:
                    break
                page += 1
            return all_groups
        except Exception as e:
            self.client._logger.error(f"Erreur lors de la récupération des groupes: {e}")
            return []
