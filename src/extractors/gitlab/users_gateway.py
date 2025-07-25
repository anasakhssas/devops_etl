"""
Module contenant la passerelle pour l'accès aux utilisateurs GitLab.
"""
from typing import Any, Dict, List, Optional

from src.extractors.gitlab.gitlab_client_improved import GitLabClient


class GitLabUsersGateway:
    """
    Passerelle pour accéder aux utilisateurs et leurs données associées dans GitLab.
    Cette classe est spécialisée dans la récupération des données relatives aux utilisateurs.
    """

    def __init__(self, gitlab_client: GitLabClient):
        """
        Initialise la passerelle avec un client GitLab.
        
        Args:
            gitlab_client: Instance du client GitLab pour effectuer les requêtes API.
        """
        self.client = gitlab_client

    def get_users(self, params: Optional[Dict[str, Any]] = None, updated_after: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Récupère la liste des utilisateurs selon les critères fournis, extraction incrémentielle possible.
        
        Args:
            params: Dictionnaire de paramètres pour filtrer les utilisateurs.
                   Exemples: 
                   - active=True (utilisateurs actifs uniquement)
                   - search="nom" (recherche par nom ou email)
                   - username="username" (recherche par nom d'utilisateur)
                   - external=True (utilisateurs externes uniquement)
            updated_after: Date de mise à jour au format "YYYY-MM-DD" (extraction incrémentielle)
        Returns:
            Liste de dictionnaires représentant les utilisateurs.
        """
        params = params.copy() if params else {}
        if updated_after:
            params["updated_after"] = updated_after
        try:
            # S'assurer que le client est connecté
            if not self.client.is_connected:
                self.client.connect()
            users_list = self.client._gitlab_client.users.list(**params)
            return [user.attributes for user in users_list]
        except Exception as e:
            self.client._logger.error(f"Erreur lors de la récupération des utilisateurs: {e}")
            return []

    def get_user(self, user_id: int) -> Dict[str, Any]:
        """
        Récupère les détails d'un utilisateur spécifique.
        
        Args:
            user_id: Identifiant de l'utilisateur à récupérer.
            
        Returns:
            Dictionnaire représentant les détails de l'utilisateur.
        """
        try:
            if not self.client.is_connected:
                self.client.connect()
            endpoint = f"/users/{user_id}"
            return self.client._make_request("GET", endpoint)
        except Exception as e:
            self.client._logger.error(f"Erreur lors de la récupération de l'utilisateur {user_id}: {e}")
            return {}

    def get_current_user(self) -> Dict[str, Any]:
        """
        Récupère les informations sur l'utilisateur actuellement authentifié.
        
        Returns:
            Dictionnaire représentant les détails de l'utilisateur courant.
        """
        try:
            if not self.client.is_connected:
                self.client.connect()
            if hasattr(self.client._gitlab_client, 'user') and self.client._gitlab_client.user:
                user = self.client._gitlab_client.user
                return {
                    'id': user.id,
                    'username': user.username,
                    'name': user.name,
                    'email': user.email,
                    'is_admin': user.is_admin,
                    'state': user.state,
                    'web_url': user.web_url,
                    'created_at': user.created_at,
                    'last_activity_on': user.last_activity_on
                }
            else:
                return self.client._make_request("GET", "/user")
        except Exception as e:
            self.client._logger.error(f"Erreur lors de la récupération de l'utilisateur courant: {e}")
            return {}

    def get_user_projects(self, user_id: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Récupère les projets d'un utilisateur spécifique.
        
        Args:
            user_id: Identifiant de l'utilisateur.
            params: Paramètres de filtrage comme:
                   - visibility="public" (visibilité: public, internal, private)
                   - simple=True (informations simplifiées)
                   - membership=True (projets où l'utilisateur est membre)
                   
        Returns:
            Liste de dictionnaires représentant les projets de l'utilisateur.
        """
        try:
            if not self.client.is_connected:
                self.client.connect()
            endpoint = f"/users/{user_id}/projects"
            return self.client._get_paginated_results(endpoint, params=params or {})
        except Exception as e:
            self.client._logger.error(f"Erreur lors de la récupération des projets de l'utilisateur {user_id}: {e}")
            return []

    def get_user_groups(self, user_id: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Récupère les groupes d'un utilisateur spécifique.
        
        Args:
            user_id: Identifiant de l'utilisateur.
            params: Paramètres de filtrage.
                   
        Returns:
            Liste de dictionnaires représentant les groupes de l'utilisateur.
        """
        try:
            if not self.client.is_connected:
                self.client.connect()
            endpoint = f"/users/{user_id}/groups"
            return self.client._get_paginated_results(endpoint, params=params or {})
        except Exception as e:
            self.client._logger.error(f"Erreur lors de la récupération des groupes de l'utilisateur {user_id}: {e}")
            return []
    
    def get_user_events(self, user_id: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Récupère les événements d'activité d'un utilisateur spécifique.
        
        Args:
            user_id: Identifiant de l'utilisateur.
            params: Paramètres de filtrage comme:
                   - action="pushed" (type d'action: pushed, commented, etc.)
                   - after="YYYY-MM-DD" (événements après date)
                   - before="YYYY-MM-DD" (événements avant date)
                   
        Returns:
            Liste de dictionnaires représentant les événements de l'utilisateur.
        """
        try:
            if not self.client.is_connected:
                self.client.connect()
            endpoint = f"/users/{user_id}/events"
            return self.client._get_paginated_results(endpoint, params=params or {})
        except Exception as e:
            self.client._logger.error(f"Erreur lors de la récupération des événements de l'utilisateur {user_id}: {e}")
            return []
        
