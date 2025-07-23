"""
Module client SonarQube pour l'extraction des données via l'API SonarQube.

Ce module fournit une interface pour interagir avec l'API SonarQube,
en gérant l'authentification, la pagination et la gestion des erreurs.
"""

import logging
import base64
from typing import Any, Dict, Generator, List, Optional, Union, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.core.exceptions import (
    APIAuthenticationError,
    APIRateLimitError,
    ConnectionError,
    ResourceNotFoundError,
)

logger = logging.getLogger(__name__)


class SonarQubeClient:
    """
    Client pour interagir avec l'API SonarQube.

    Cette classe encapsule toutes les interactions avec l'API SonarQube,
    y compris l'authentification, la gestion des erreurs et la pagination.
    """

    def __init__(
        self,
        api_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_backoff_factor: float = 0.3,
    ) -> None:
        """
        Initialiser le client SonarQube avec les paramètres de connexion.

        Args:
            api_url: URL de base de l'API SonarQube (ex: https://sonarqube.example.com/api)
            username: Nom d'utilisateur pour l'authentification basique (non utilisé si token est fourni)
            password: Mot de passe pour l'authentification basique (non utilisé si token est fourni)
            token: Token d'authentification (recommandé)
            timeout: Délai d'attente maximum pour les requêtes en secondes
            max_retries: Nombre maximum de tentatives pour les requêtes en échec
            retry_backoff_factor: Facteur de délai exponentiel entre les tentatives
        """
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
        
        # Configuration de la session avec retry automatique
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=retry_backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Configuration de l'authentification
        if token:
            # Utilisation du token comme nom d'utilisateur avec mot de passe vide (méthode recommandée)
            auth_string = f"{token}:"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            self.session.headers.update({
                "Authorization": f"Basic {encoded_auth}",
                "Accept": "application/json",
            })
        elif username and password:
            # Authentification basique avec nom d'utilisateur et mot de passe
            self.session.auth = (username, password)
            self.session.headers.update({
                "Accept": "application/json",
            })
        else:
            logger.warning("No authentication provided for SonarQube API. Some endpoints may not be accessible.")
            self.session.headers.update({
                "Accept": "application/json",
            })
        
        logger.info(f"SonarQube client initialized with API URL: {api_url}")

    def test_connection(self) -> bool:
        """
        Tester la connexion à l'API SonarQube.

        Returns:
            bool: True si la connexion est établie avec succès, sinon False

        Raises:
            APIAuthenticationError: Si l'authentification échoue
            ConnectionError: Si la connexion échoue pour d'autres raisons
        """
        try:
            # Utilisation du endpoint /system/status qui est léger et disponible pour tous les utilisateurs authentifiés
            response = self.session.get(f"{self.api_url}/system/status", timeout=self.timeout)
            
            if response.status_code == 401:
                raise APIAuthenticationError("SonarQube authentication failed. Check your credentials.")
            
            response.raise_for_status()
            status_info = response.json()
            
            logger.info(f"Successfully connected to SonarQube API. Status: {status_info.get('status', 'unknown')}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to SonarQube API: {str(e)}")
            raise ConnectionError(f"Could not connect to SonarQube API: {str(e)}")

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, paginate: bool = False
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Effectuer une requête GET vers l'API SonarQube.

        Args:
            endpoint: Point de terminaison de l'API (sans l'URL de base)
            params: Paramètres optionnels de la requête
            paginate: Si True, gère automatiquement la pagination pour récupérer toutes les pages

        Returns:
            Les données de la réponse JSON

        Raises:
            APIAuthenticationError: Si l'authentification échoue
            APIRateLimitError: Si la limite de taux d'API est atteinte
            ResourceNotFoundError: Si la ressource demandée n'est pas trouvée
            ConnectionError: Pour les autres erreurs de connexion
        """
        if paginate:
            result = list(self._paginated_get(endpoint, params or {}))
            return result
        
        return self._make_request("GET", endpoint, params)

    def _paginated_get(
        self, endpoint: str, params: Dict[str, Any]
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Générateur pour récupérer toutes les pages d'une ressource paginée.

        Args:
            endpoint: Point de terminaison de l'API
            params: Paramètres de la requête

        Yields:
            Chaque élément individuel de toutes les pages de réponse
        """
        # Paramètres de pagination SonarQube (peut varier selon l'endpoint)
        # Certains endpoints utilisent p/ps (page/page size) d'autres utilisent pageIndex/pageSize
        if "ps" not in params and "pageSize" not in params:
            # Utiliser ps par défaut, qui est le plus courant
            params["ps"] = 100  # Maximiser le nombre d'éléments par page
        
        page = 1
        has_more = True
        
        while has_more:
            # Ajuster les paramètres de page en fonction de l'endpoint
            if "pageIndex" in params or any(key.startswith("pageIndex") for key in params):
                params["pageIndex"] = page
            else:
                params["p"] = page
                
            response_data = self._make_request("GET", endpoint, params)
            
            # SonarQube peut retourner les résultats dans différentes structures
            # Vérifier les différents formats de pagination courants
            if "paging" in response_data:
                # Format standard avec un objet paging
                paging = response_data.get("paging", {})
                total = paging.get("total", 0)
                page_size = paging.get("pageSize", 100)
                current_page = paging.get("pageIndex", page)
                
                # Déterminer la clé qui contient les données (components, issues, etc.)
                # Trouver la clé qui contient la liste de résultats
                result_keys = [k for k, v in response_data.items() if isinstance(v, list) and k != "paging"]
                if result_keys:
                    result_key = result_keys[0]
                    items = response_data.get(result_key, [])
                    
                    for item in items:
                        yield item
                    
                    # Vérifier s'il y a d'autres pages
                    has_more = (current_page * page_size) < total
                else:
                    # Pas de données trouvées dans un format reconnaissable
                    has_more = False
            elif isinstance(response_data, list):
                # Certains endpoints retournent directement une liste
                if not response_data:
                    has_more = False
                
                for item in response_data:
                    yield item
                
                # Pour les endpoints qui retournent une liste sans info de pagination
                # On suppose qu'il n'y a plus de pages si on reçoit moins que la taille demandée
                has_more = len(response_data) >= params.get("ps", params.get("pageSize", 100))
            else:
                # Format non reconnu ou non paginé
                yield response_data
                has_more = False
            
            page += 1
            logger.debug(f"Fetching page {page} for endpoint {endpoint}")

    def _make_request(
        self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, data: Any = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Effectuer une requête HTTP vers l'API SonarQube avec gestion des erreurs.

        Args:
            method: Méthode HTTP (GET, POST, PUT, DELETE)
            endpoint: Point de terminaison de l'API
            params: Paramètres optionnels de la requête
            data: Données optionnelles du corps de la requête

        Returns:
            Les données de la réponse JSON

        Raises:
            APIAuthenticationError: Si l'authentification échoue
            APIRateLimitError: Si la limite de taux d'API est atteinte
            ResourceNotFoundError: Si la ressource demandée n'est pas trouvée
            ConnectionError: Pour les autres erreurs de connexion
        """
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(f"Making {method} request to {url}")
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 401:
                raise APIAuthenticationError("SonarQube authentication failed. Check your credentials.")
            elif response.status_code == 403:
                raise APIAuthenticationError("Insufficient permissions to access this resource.")
            elif response.status_code == 404:
                raise ResourceNotFoundError(f"Resource not found: {url}")
            elif response.status_code == 429:
                raise APIRateLimitError("SonarQube API rate limit exceeded. Please try again later.")
            
            response.raise_for_status()
            
            # Certains endpoints peuvent retourner une réponse vide avec succès
            if not response.content:
                return {}
                
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to SonarQube API: {str(e)}")
            raise ConnectionError(f"Error connecting to SonarQube API: {str(e)}")
