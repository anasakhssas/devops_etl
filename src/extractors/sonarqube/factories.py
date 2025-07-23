"""
Module de fabrique pour les extracteurs SonarQube.

Ce module fournit des fonctionnalités pour créer facilement
des instances d'extracteurs SonarQube.
"""

import logging
from typing import Dict, Optional

from src.core.config import ConfigManager
from src.extractors.sonarqube.sonarqube_client import SonarQubeClient
from src.extractors.sonarqube.projects_gateway import SonarQubeProjectsGateway

logger = logging.getLogger(__name__)


class SonarQubeClientFactory:
    """
    Fabrique pour créer des instances de clients SonarQube.
    """
    
    @staticmethod
    def create_client(
        config: Optional[Dict] = None,
        api_url: Optional[str] = None,
        token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ) -> SonarQubeClient:
        """
        Créer une instance de SonarQubeClient à partir de la configuration.
        
        Args:
            config: Configuration SonarQube personnalisée (optionnel)
            api_url: URL de l'API SonarQube (optionnel, remplace la config)
            token: Token d'authentification SonarQube (optionnel, remplace la config)
            username: Nom d'utilisateur SonarQube (optionnel, remplace la config)
            password: Mot de passe SonarQube (optionnel, remplace la config)
            timeout: Délai d'attente en secondes (optionnel, remplace la config)
            max_retries: Nombre maximal de tentatives (optionnel, remplace la config)
            
        Returns:
            SonarQubeClient: Instance configurée du client SonarQube
        """
        if config is None:
            config_manager = ConfigManager()
            config = config_manager.get_section("sonarqube")
            
        # Utiliser les paramètres fournis ou les valeurs de configuration
        final_api_url = api_url or config.get("api_url")
        final_token = token or config.get("token")
        final_username = username or config.get("username")
        final_password = password or config.get("password")
        final_timeout = timeout or config.get("timeout", 30)
        final_max_retries = max_retries or config.get("max_retries", 3)
        
        if not final_api_url:
            raise ValueError("L'URL de l'API SonarQube n'est pas définie")
            
        # Créer le client avec les paramètres déterminés
        client_params = {
            "api_url": final_api_url,
            "timeout": final_timeout,
            "max_retries": final_max_retries,
        }
        
        # Privilégier l'authentification par token si disponible
        if final_token:
            client_params["token"] = final_token
        elif final_username and final_password:
            client_params["username"] = final_username
            client_params["password"] = final_password
        else:
            logger.warning("Aucune méthode d'authentification fournie pour SonarQube")
            
        logger.info(f"Création d'un client SonarQube pour {final_api_url}")
        return SonarQubeClient(**client_params)


class SonarQubeGatewayFactory:
    """
    Fabrique pour créer des instances de passerelles SonarQube.
    """
    
    @staticmethod
    def create_projects_gateway(client: Optional[SonarQubeClient] = None) -> SonarQubeProjectsGateway:
        """
        Créer une instance de SonarQubeProjectsGateway.
        
        Args:
            client: Instance de SonarQubeClient (optionnel, créé automatiquement si non fourni)
            
        Returns:
            SonarQubeProjectsGateway: Instance de la passerelle de projets SonarQube
        """
        if client is None:
            client = SonarQubeClientFactory.create_client()
            
        logger.info("Création d'une passerelle de projets SonarQube")
        return SonarQubeProjectsGateway(client)
