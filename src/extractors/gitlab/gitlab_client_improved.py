"""
Client GitLab optimisé avec conventions de nomenclature améliorées.

Ce module fournit un client GitLab suivant les meilleures pratiques
de nomenclature et de structuration du code Python.
"""
import gitlab
import logging
import ssl
import time
from typing import Any, Dict, List, Optional, Union

import urllib3
from urllib3.exceptions import InsecureRequestWarning

from src.core.constants import (
    DEFAULT_GITLAB_TIMEOUT,
    DEFAULT_GITLAB_MAX_RETRIES,
    DEFAULT_GITLAB_RETRY_DELAY,
    DEFAULT_GITLAB_ITEMS_PER_PAGE,
    SUPPORTED_GITLAB_RESOURCES,
    SSL_CONFIG,
    ERROR_MESSAGES,
    SUCCESS_MESSAGES
)
from src.core.exceptions import APIAuthenticationError, APIConnectionError, APIRateLimitError


class GitLabClient:
    """
    Client GitLab avec conventions de nomenclature améliorées.
    
    Ce client fournit une interface standardisée pour extraire les données GitLab
    avec une nomenclature cohérente et des bonnes pratiques de développement.
    """

    def __init__(self, gitlab_config: Dict[str, Any]) -> None:
        """
        Initialise le client GitLab avec une configuration validée.
        
        Args:
            gitlab_config: Configuration GitLab avec clés requises et optionnelles
        
        Raises:
            ValueError: Si la configuration est invalide
        """
        self._logger = logging.getLogger(__name__)
        
        # Configuration avec validation
        self._validate_configuration(gitlab_config)
        self._extract_configuration_parameters(gitlab_config)
        
        # Configuration SSL
        self._configure_ssl_settings()
        
        # État de la connexion
        self._gitlab_client: Optional[gitlab.Gitlab] = None
        self._current_user_info: Optional[Dict[str, Any]] = None
        self._connection_status = False
    
    def _validate_configuration(self, config: Dict[str, Any]) -> None:
        """
        Valide la configuration GitLab fournie.
        
        Args:
            config: Configuration à valider
            
        Raises:
            ValueError: Si des paramètres obligatoires sont manquants
        """
        required_parameters = ['api_url', 'private_token']
        missing_parameters = [
            param for param in required_parameters 
            if not config.get(param)
        ]
        
        if missing_parameters:
            raise ValueError(
                ERROR_MESSAGES["MISSING_CONFIG"].format(
                    parameter=", ".join(missing_parameters)
                )
            )
    
    def _extract_configuration_parameters(self, config: Dict[str, Any]) -> None:
        """
        Extrait et assigne les paramètres de configuration.
        
        Args:
            config: Configuration GitLab
        """
        self._api_url = config["api_url"]
        self._private_token = config["private_token"]
        self._request_timeout = config.get("timeout", DEFAULT_GITLAB_TIMEOUT)
        self._max_retry_attempts = config.get("max_retries", DEFAULT_GITLAB_MAX_RETRIES)
        self._retry_delay_seconds = config.get("retry_delay", DEFAULT_GITLAB_RETRY_DELAY)
        self._items_per_page = config.get("items_per_page", DEFAULT_GITLAB_ITEMS_PER_PAGE)
        self._ssl_verification_enabled = config.get("verify_ssl", SSL_CONFIG["VERIFY_SSL_DEFAULT"])
        
        # Configuration proxy
        self._proxy_settings = self._extract_proxy_configuration(config.get("proxy", {}))
    
    def _extract_proxy_configuration(self, proxy_config: Dict[str, Any]) -> Dict[str, str]:
        """
        Extrait et valide la configuration proxy.
        
        Args:
            proxy_config: Configuration proxy
            
        Returns:
            Configuration proxy validée
        """
        proxy_settings = {}
        
        if proxy_config:
            if proxy_config.get("http"):
                proxy_settings["http"] = proxy_config["http"]
            if proxy_config.get("https"):
                proxy_settings["https"] = proxy_config["https"]
            
            if proxy_settings:
                self._logger.info(f"Configuration proxy détectée: {list(proxy_settings.keys())}")
        
        return proxy_settings
    
    def _configure_ssl_settings(self) -> None:
        """Configure les paramètres SSL selon la configuration."""
        if not self._ssl_verification_enabled:
            urllib3.disable_warnings(InsecureRequestWarning)
            ssl._create_default_https_context = ssl._create_unverified_context
            self._logger.warning(SSL_CONFIG["SSL_WARNING_MESSAGE"])
            self._logger.info("Configuration SSL adaptée pour les certificats d'entreprise.")
    
    def establish_connection(self) -> bool:
        """
        Établit la connexion avec l'API GitLab.
        
        Returns:
            True si la connexion est établie, False sinon
            
        Raises:
            APIAuthenticationError: Si l'authentification échoue
            APIConnectionError: Si la connexion échoue
        """
        try:
            self._gitlab_client = self._create_gitlab_client()
            self._authenticate_user()
            self._connection_status = True
            
            self._logger.info(
                SUCCESS_MESSAGES["CONNECTION_ESTABLISHED"].format(
                    service=f"GitLab ({self._current_user_info['username']})"
                )
            )
            return True
            
        except gitlab.exceptions.GitlabAuthenticationError as auth_error:
            self._connection_status = False
            error_message = ERROR_MESSAGES["AUTHENTICATION_FAILED"].format(
                service="GitLab", error=str(auth_error)
            )
            self._logger.error(error_message)
            raise APIAuthenticationError(error_message)
            
        except gitlab.exceptions.GitlabConnectionError as connection_error:
            self._connection_status = False
            error_message = ERROR_MESSAGES["CONNECTION_FAILED"].format(
                service="GitLab", error=str(connection_error)
            )
            self._logger.error(error_message)
            raise APIConnectionError(error_message)
            
        except Exception as unexpected_error:
            self._connection_status = False
            error_message = ERROR_MESSAGES["API_ERROR"].format(
                service="GitLab", error=str(unexpected_error)
            )
            self._logger.error(error_message)
            raise APIConnectionError(error_message)
    
    def _create_gitlab_client(self) -> gitlab.Gitlab:
        """Crée et configure le client GitLab."""
        import re
        base_url = self._api_url.rstrip('/')
        # Supprime tous les '/api/v4' finaux pour donner l'URL racine à python-gitlab
        base_url = re.sub(r'(/api/v4)+$', '', base_url)
        base_url = base_url.rstrip('/')
        print(f"[DEBUG] GitLab base_url utilisé: {base_url}")  # Debug temporaire

        gitlab_client = gitlab.Gitlab(
            url=base_url,
            private_token=self._private_token,
            ssl_verify=self._ssl_verification_enabled,
            timeout=self._request_timeout
        )
        if self._proxy_settings:
            gitlab_client.session.proxies.update(self._proxy_settings)
        return gitlab_client
    
    def _authenticate_user(self) -> None:
        """
        Authentifie l'utilisateur et stocke les informations.
        
        Raises:
            gitlab.exceptions.GitlabAuthenticationError: Si l'authentification échoue
        """
        self._gitlab_client.auth()
        current_user = self._gitlab_client.user
        
        self._current_user_info = {
            'user_id': current_user.id,
            'username': current_user.username,
            'full_name': current_user.name,
            'email_address': current_user.email,
            'is_administrator': getattr(current_user, 'is_admin', False)
        }
    
    def validate_connection(self) -> Dict[str, Any]:
        """
        Valide la connexion GitLab et retourne les informations détaillées.
        
        Returns:
            Dictionnaire contenant les informations de validation
        """
        validation_result = {
            "connection_successful": False,
            "api_endpoint": self._api_url
        }
        
        try:
            # Créer le client si nécessaire
            if self._gitlab_client is None:
                self._gitlab_client = self._create_gitlab_client()
            
            # Récupérer les informations de version
            version_information = self._get_version_information()
            validation_result.update(version_information)
            
            # Tester l'authentification
            self._authenticate_user()
            validation_result["user_information"] = self._current_user_info
            validation_result["connection_successful"] = True
            
            self._logger.info(
                f"Validation GitLab réussie: Version={version_information.get('gitlab_version', 'N/A')}, "
                f"Utilisateur={self._current_user_info['username']}"
            )
            
        except gitlab.exceptions.GitlabAuthenticationError as auth_error:
            validation_result["error_message"] = f"Erreur d'authentification: {str(auth_error)}"
            self._logger.error(f"Validation GitLab échouée (authentification): {auth_error}")
            
        except Exception as general_error:
            validation_result["error_message"] = f"Erreur d'accès API: {str(general_error)}"
            self._logger.error(f"Validation GitLab échouée: {general_error}")
        
        return validation_result
    
    def _get_version_information(self) -> Dict[str, Any]:
        """Récupère les informations de version GitLab de manière robuste."""
        try:
            version_info = self._gitlab_client.version()
        
            # Gestion des différents formats de réponse
            if isinstance(version_info, tuple):  # Anciennes versions python-gitlab
                return {
                    "gitlab_version": version_info[0],
                    "api_version": version_info[1].get("version"),
                    "revision": version_info[1].get("revision")
                }
            elif isinstance(version_info, dict):  # Nouvelles versions
                return {
                    "gitlab_version": version_info.get("version"),
                    "api_version": version_info.get("api_version"),
                    "revision": version_info.get("revision")
                }
            return {}
        except Exception as e:
            self._logger.warning(f"Failed to get GitLab version: {str(e)}")
        return {}
    
    def extract_gitlab_users(self, active_users_only: bool = False, 
                           include_bot_accounts: bool = True, 
                           items_per_page: int = None) -> List[Dict[str, Any]]:
        """
        Extrait les utilisateurs GitLab avec options de filtrage.
        
        Args:
            active_users_only: Si True, ne récupère que les utilisateurs actifs
            include_bot_accounts: Si True, inclut les comptes bots
            items_per_page: Nombre d'éléments par page
            
        Returns:
            Liste des utilisateurs GitLab
            
        Raises:
            APIConnectionError: Si une erreur de connexion survient
        """
        if self._gitlab_client is None:
            self.establish_connection()
        
        request_parameters = {}
        
        # Filtrage par statut actif
        if active_users_only:
            request_parameters["active"] = True
        
        # Configuration de la pagination
        if items_per_page:
            request_parameters["per_page"] = items_per_page
        else:
            request_parameters["per_page"] = self._items_per_page
        
        try:
            # Récupération des utilisateurs
            gitlab_users = self._gitlab_client.users.list(get_all=True, **request_parameters)
            
            # Conversion et filtrage
            processed_users = []
            for gitlab_user in gitlab_users:
                user_dictionary = self._convert_gitlab_object_to_dict(gitlab_user)
                
                # Filtrage des bots si demandé
                if not include_bot_accounts and user_dictionary.get('bot', False):
                    continue
                
                processed_users.append(user_dictionary)
            
            self._logger.info(f"Récupération de {len(processed_users)} utilisateurs GitLab")
            return processed_users
            
        except gitlab.exceptions.GitlabListError as list_error:
            error_message = ERROR_MESSAGES["API_ERROR"].format(
                service="GitLab Users", error=str(list_error)
            )
            self._logger.error(error_message)
            raise APIConnectionError(error_message)
    
    def extract_gitlab_projects(self, owned_projects_only: bool = False,
                              starred_projects_only: bool = False,
                              project_visibility: str = None,
                              items_per_page: int = None) -> List[Dict[str, Any]]:
        """
        Extrait les projets GitLab avec options de filtrage.
        
        Args:
            owned_projects_only: Si True, ne récupère que les projets possédés
            starred_projects_only: Si True, ne récupère que les projets favoris
            project_visibility: Niveau de visibilité ('public', 'internal', 'private')
            items_per_page: Nombre d'éléments par page
            
        Returns:
            Liste des projets GitLab
        """
        if self._gitlab_client is None:
            self.establish_connection()
        
        request_parameters = {}
        
        if owned_projects_only:
            request_parameters["owned"] = True
        if starred_projects_only:
            request_parameters["starred"] = True
        if project_visibility:
            request_parameters["visibility"] = project_visibility
        if items_per_page:
            request_parameters["per_page"] = items_per_page
        else:
            request_parameters["per_page"] = self._items_per_page
        
        try:
            gitlab_projects = self._gitlab_client.projects.list(get_all=True, **request_parameters)
            processed_projects = [
                self._convert_gitlab_object_to_dict(project) 
                for project in gitlab_projects
            ]
            
            self._logger.info(f"Récupération de {len(processed_projects)} projets GitLab")
            return processed_projects
            
        except gitlab.exceptions.GitlabListError as list_error:
            error_message = ERROR_MESSAGES["API_ERROR"].format(
                service="GitLab Projects", error=str(list_error)
            )
            self._logger.error(error_message)
            raise APIConnectionError(error_message)
    
    def extract_gitlab_resource(self, resource_type: str, 
                              resource_id: Optional[int] = None,
                              additional_parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Extrait une ressource GitLab générique.
        
        Args:
            resource_type: Type de ressource à extraire
            resource_id: ID spécifique (optionnel)
            additional_parameters: Paramètres additionnels
            
        Returns:
            Liste des ressources extraites
            
        Raises:
            ValueError: Si le type de ressource n'est pas supporté
            APIConnectionError: Si une erreur d'extraction survient
        """
        if resource_type not in SUPPORTED_GITLAB_RESOURCES:
            raise ValueError(
                f"Type de ressource '{resource_type}' non supporté. "
                f"Types supportés: {SUPPORTED_GITLAB_RESOURCES}"
            )
        
        if self._gitlab_client is None:
            self.establish_connection()
        
        try:
            resource_manager = self._get_resource_manager(resource_type)
            
            if resource_id:
                return self._extract_single_resource(resource_manager, resource_id, additional_parameters)
            else:
                return self._extract_resource_list(resource_manager, resource_type, additional_parameters)
                
        except Exception as extraction_error:
            error_message = ERROR_MESSAGES["API_ERROR"].format(
                service=f"GitLab {resource_type}", error=str(extraction_error)
            )
            self._logger.error(error_message)
            raise APIConnectionError(error_message)
    
    def _get_resource_manager(self, resource_type: str):
        """
        Récupère le gestionnaire de ressources GitLab approprié.
        
        Args:
            resource_type: Type de ressource
            
        Returns:
            Gestionnaire de ressources GitLab
        """
        resource_manager_mapping = {
            "users": self._gitlab_client.users,
            "projects": self._gitlab_client.projects,
            "groups": self._gitlab_client.groups,
            "issues": self._gitlab_client.issues,
            "merge_requests": self._gitlab_client.mergerequests,
        }
        
        return resource_manager_mapping.get(resource_type)
    
    def _extract_single_resource(self, resource_manager, resource_id: int, 
                                parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrait une ressource unique par ID.
        
        Args:
            resource_manager: Gestionnaire de ressources
            resource_id: ID de la ressource
            parameters: Paramètres additionnels
            
        Returns:
            Liste contenant la ressource unique
        """
        try:
            resource_item = resource_manager.get(resource_id, **(parameters or {}))
            return [self._convert_gitlab_object_to_dict(resource_item)]
        except gitlab.exceptions.GitlabGetError as get_error:
            self._logger.error(f"Erreur lors de la récupération de la ressource {resource_id}: {get_error}")
            return []
    
    def _extract_resource_list(self, resource_manager, resource_type: str, 
                             parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrait une liste de ressources avec pagination.
        
        Args:
            resource_manager: Gestionnaire de ressources
            resource_type: Type de ressource
            parameters: Paramètres additionnels
            
        Returns:
            Liste des ressources extraites
        """
        try:
            resource_items = resource_manager.list(get_all=True, **(parameters or {}))
            return [self._convert_gitlab_object_to_dict(item) for item in resource_items]
        except gitlab.exceptions.GitlabListError as list_error:
            self._logger.error(f"Erreur lors de la récupération de la liste {resource_type}: {list_error}")
            return []
    
    def _convert_gitlab_object_to_dict(self, gitlab_object) -> Dict[str, Any]:
        """
        Convertit un objet GitLab en dictionnaire.
        
        Args:
            gitlab_object: Objet GitLab à convertir
            
        Returns:
            Dictionnaire représentant l'objet
        """
        if hasattr(gitlab_object, 'attributes'):
            return gitlab_object.attributes
        elif hasattr(gitlab_object, '__dict__'):
            return {
                key: value 
                for key, value in gitlab_object.__dict__.items() 
                if not key.startswith('_')
            }
        else:
            return gitlab_object
    
    def close_connection(self) -> None:
        """
        Ferme la connexion et libère les ressources.
        """
        self._connection_status = False
        self._gitlab_client = None
        self._current_user_info = None
    
    @property
    def is_connected(self) -> bool:
        """
        Indique si la connexion est établie.
        
        Returns:
            True si connecté, False sinon
        """
        return self._connection_status
    
    @property
    def current_user_info(self) -> Optional[Dict[str, Any]]:
        """
        Retourne les informations de l'utilisateur actuel.
        
        Returns:
            Informations utilisateur ou None si non connecté
        """
        return self._current_user_info
    

    #-----------------
    def connect(self) -> bool:
        """Méthode alias pour établir la connexion (utilisé par les tests)."""
        return self.establish_connection()

    def test_connection(self) -> Dict[str, Any]:
        try:
            user = self._gitlab_client.user
            gitlab_version = self._get_gitlab_version()
            return {
                "connection_successful": True,
                "user_information": user.attributes,
                "gitlab_version": gitlab_version
            }
        except Exception as e:
            return {
                "connection_successful": False,
                "error_message": str(e),
                "user_information": None,
                "gitlab_version": None
            }

    def _get_gitlab_version(self) -> Optional[str]:
        try:
            version_info = self._gitlab_client.version()
            return version_info.get("version", "unknown") if isinstance(version_info, dict) else "unknown"
        except Exception as e:
            print(f"Impossible de récupérer la version GitLab: {e}")
            return "unknown"

    def get_project_commits(self, project_id: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Récupère les commits d'un projet GitLab.
        Args:
            project_id: ID du projet
            params: paramètres optionnels pour filtrer les commits
        Returns:
            Liste de commits (dictionnaires)
        """
        if self._gitlab_client is None:
            self.establish_connection()
        try:
            project = self._gitlab_client.projects.get(project_id)
            commits = project.commits.list(get_all=True, **(params or {}))
            return [self._convert_gitlab_object_to_dict(commit) for commit in commits]
        except Exception as e:
            self._logger.error(f"Erreur lors de la récupération des commits du projet {project_id}: {e}")
            return []


