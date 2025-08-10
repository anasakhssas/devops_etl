"""
Module de fabrique pour les extracteurs SonarQube.

Ce module fournit des fonctionnalités pour créer facilement
des instances d'extracteurs SonarQube.
"""

import logging
from typing import Dict, Optional
# Ajouts:
from typing import Any, List
from src.extractors.base_extractor import BaseExtractor
from src.core.exceptions import ExtractionError

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

class SonarQubeExtractor(BaseExtractor):
    """
    Extracteur SonarQube basé sur BaseExtractor.
    Orchestration de l'extraction des projets, métriques, issues, branches, etc.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        try:
            self.client = SonarQubeClientFactory.create_client(config=config)
            self.projects = SonarQubeGatewayFactory.create_projects_gateway(self.client)
        except Exception as e:
            raise ExtractionError(f"Erreur d'initialisation SonarQubeExtractor: {e}")

    def connect(self) -> bool:
        try:
            ok = self.client.test_connection()
            self.is_connected = bool(ok)
            return self.is_connected
        except Exception as e:
            raise ExtractionError(f"Échec de connexion SonarQube: {e}")

    def test_connection(self) -> Dict[str, Any]:
        try:
            status = self.client.test_connection()
            return {"status": "ok" if status else "failed"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def extract(
        self,
        organization: Optional[str] = None,
        project_keys: Optional[List[str]] = None,
        include_issues: bool = True,
        include_branches: bool = True,
        include_quality_gate: bool = True,
        include_activity: bool = False,
        branch: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extraction "full" par projet: détails, métriques (qualité + couverture), issues, branches, quality gate, activité CE.
        """
        if not self.is_connected and not self.connect():
            raise ExtractionError("Non connecté à SonarQube.")

        # Métriques intéressantes par défaut
        quality_metrics = [
            "bugs","reliability_rating","vulnerabilities","security_rating","security_hotspots",
            "security_hotspots_reviewed","code_smells","sqale_index","sqale_debt_ratio",
            "sqale_rating",
            "duplicated_lines_density","duplicated_blocks",
            "cognitive_complexity","complexity",
        ]
        coverage_metrics = [
            "coverage","line_coverage","branch_coverage","uncovered_lines","lines_to_cover",
            "uncovered_conditions","conditions_to_cover","tests","test_success_density",
            "test_failures","test_errors","skipped_tests","test_execution_time",
        ]
        all_metrics = quality_metrics + coverage_metrics

        projects = self.projects.get_projects(organization=organization, project_keys=project_keys)
        results: List[Dict[str, Any]] = []

        for comp in projects:
            proj_key = comp.get("key") or comp.get("project", {}).get("key")
            if not proj_key:
                continue

            item: Dict[str, Any] = {"project": comp}

            # Mesures globales du projet
            item["measures"] = self.projects.get_project_metrics(proj_key, all_metrics, branch=branch)

            # Issues du projet (optionnel)
            if include_issues:
                item["issues"] = self.projects.get_project_issues(
                    proj_key,
                    branch=branch,
                )

            # Branches (optionnel)
            if include_branches:
                item["branches"] = self.projects.get_project_branches(proj_key)

            # Quality Gate (optionnel)
            if include_quality_gate:
                item["quality_gate"] = self.projects.get_quality_gate_status(proj_key, branch=branch)

            # Activité CE (optionnel)
            if include_activity:
                item["ce_activity"] = self.projects.get_compute_engine_activity(proj_key, branch=branch, only_current=False)

            results.append(item)

        return results

    def extract_incremental(
        self,
        from_date: str,
        to_date: Optional[str] = None,
        project_keys: Optional[List[str]] = None,
        branch: Optional[str] = None,
        include_history_metrics: bool = True,
        include_new_issues: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Extraction incrémentielle:
        - Historique des mesures depuis from_date (optionnellement jusqu'à to_date)
        - Issues créées/maj depuis from_date
        """
        if not self.is_connected and not self.connect():
            raise ExtractionError("Non connecté à SonarQube.")

        projects = self.projects.get_projects(project_keys=project_keys)
        results: List[Dict[str, Any]] = []

        # Métriques par défaut pour l'historique
        history_metrics = [
            "bugs","vulnerabilities","code_smells","coverage","duplicated_lines_density"
        ]

        for comp in projects:
            proj_key = comp.get("key") or comp.get("project", {}).get("key")
            if not proj_key:
                continue

            inc: Dict[str, Any] = {"project": {"key": proj_key, "name": comp.get("name")}}

            if include_history_metrics:
                inc["history"] = self.projects.get_project_activity(
                    project_key=proj_key,
                    metrics=history_metrics,
                    from_date=from_date,
                    to_date=to_date,
                    branch=branch,
                )

            if include_new_issues:
                # createdAfter/createdBefore côté API, filtrage principal par from_date/to_date
                params_issues = {
                    "created_after": from_date,
                    "created_before": to_date,
                }
                # get_project_issues accepte des kwargs connus mappés -> on utilise directement les paramètres
                inc["issues"] = self.projects.get_project_issues(
                    project_key=proj_key,
                    created_after=from_date,
                    created_before=to_date,
                    branch=branch,
                )

            results.append(inc)

        return results
