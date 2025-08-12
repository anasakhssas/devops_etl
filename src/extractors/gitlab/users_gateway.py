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
        Note: l'attribut 'email' n'est renvoyé par GitLab que pour un admin et avec 'with_email=true'.

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
            if "with_email" not in params:
                params["with_email"] = True  # booléen
            endpoint = "/users"
            all_users = []
            page = 1
            while True:
                params["page"] = page
                response = self.client._gitlab_client.http_get(endpoint, params=params)
                if not response or not isinstance(response, list):
                    break

                # Enrichissement: compléter les emails manquants
                for u in response:
                    if not (u.get("email") or u.get("public_email")):
                        resolved = self._fetch_user_email(u.get("id"))
                        if resolved:
                            u["email"] = resolved

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

    def _fetch_user_email(self, user_id: Optional[int]) -> Optional[str]:
        """
        Tente de récupérer l'email d'un utilisateur via des endpoints admins.
        Ordre:
          1) GET /users/:id?with_email=true
          2) GET /users/:id/emails (prend 'primary' si disponible, sinon le premier)
        """
        if not user_id:
            return None
        try:
            # 1) Détail utilisateur avec 'with_email=true'
            detail = self.client._gitlab_client.http_get(f"/users/{user_id}", params={"with_email": True})
            if isinstance(detail, dict):
                if detail.get("email"):
                    return detail["email"]
                # parfois 'public_email' peut suffire
                if detail.get("public_email"):
                    return detail["public_email"]
        except Exception as e:
            self.client._logger.debug(f"Impossible de récupérer /users/{user_id} (with_email): {e}")

        try:
            # 2) Liste des emails de l'utilisateur
            emails = self.client._gitlab_client.http_get(f"/users/{user_id}/emails", params={"per_page": 100})
            if isinstance(emails, list) and emails:
                primary = next((em for em in emails if em.get("primary")), None)
                return (primary or emails[0]).get("email")
        except Exception as e:
            self.client._logger.debug(f"Impossible de récupérer /users/{user_id}/emails: {e}")

        return None
