"""
Module pour l'interaction avec les projets SonarQube via l'API.

Ce module fournit une passerelle (gateway) pour accéder aux projets
SonarQube et à leurs métriques associées.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from src.extractors.sonarqube.sonarqube_client import SonarQubeClient
from src.core.exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


class SonarQubeProjectsGateway:
    """
    Passerelle pour interagir avec les projets SonarQube et leurs métriques.
    
    Cette classe encapsule toutes les interactions avec les projets SonarQube,
    en utilisant le SonarQubeClient pour les requêtes API.
    """
    
    def __init__(self, sonarqube_client: SonarQubeClient) -> None:
        """
        Initialiser la passerelle de projets SonarQube.
        
        Args:
            sonarqube_client: Instance de SonarQubeClient pour les requêtes API
        """
        self.client = sonarqube_client
        logger.info("SonarQubeProjectsGateway initialized")
        
    def get_projects(
        self, 
        organization: Optional[str] = None,
        project_keys: Optional[List[str]] = None,
        analyzed_before: Optional[str] = None,
        analyzed_after: Optional[str] = None,
        q: Optional[str] = None,
        qualifiers: str = "TRK",  # TRK pour les projets, APP pour les applications, etc.
    ) -> List[Dict[str, Any]]:
        """
        Récupérer la liste des projets selon les critères spécifiés.
        
        Args:
            organization: Organisation SonarQube (optionnel)
            project_keys: Liste de clés de projet à rechercher (optionnel)
            analyzed_before: Filtrer les projets analysés avant cette date (format YYYY-MM-DD)
            analyzed_after: Filtrer les projets analysés après cette date (format YYYY-MM-DD)
            q: Terme de recherche pour filtrer les projets par nom
            qualifiers: Type d'éléments à retourner (TRK pour les projets, APP pour les applications)
            
        Returns:
            Liste des projets correspondant aux critères
        """
        params = {
            "qualifiers": qualifiers,
        }
        
        # Ajouter les paramètres optionnels uniquement s'ils sont spécifiés
        if organization:
            params["organization"] = organization
        if project_keys:
            params["projects"] = ",".join(project_keys)
        if analyzed_before:
            params["analyzedBefore"] = analyzed_before
        if analyzed_after:
            params["analyzedAfter"] = analyzed_after
        if q:
            params["q"] = q
            
        logger.info(f"Fetching projects with parameters: {params}")
        # Utilisation de l'endpoint projects/search pour récupérer la liste des projets
        response = self.client.get("projects/search", params=params, paginate=True)
        
        return response if isinstance(response, list) else response.get("components", [])
        
    def get_project(self, project_key: str) -> Dict[str, Any]:
        """
        Récupérer les détails d'un projet spécifique.
        
        Args:
            project_key: Clé du projet SonarQube
            
        Returns:
            Détails du projet
            
        Raises:
            ResourceNotFoundError: Si le projet n'existe pas
        """
        logger.info(f"Fetching details for project key: {project_key}")
        try:
            # Utilisation de l'endpoint components/show pour récupérer les détails du projet
            return self.client.get("components/show", params={"component": project_key})
        except ResourceNotFoundError:
            logger.error(f"Project with key '{project_key}' not found")
            raise ResourceNotFoundError(f"Project with key '{project_key}' not found")
            
    def get_project_metrics(
        self, 
        project_key: str, 
        metrics: List[str],
        branch: Optional[str] = None,
        additional_fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Récupérer les métriques d'un projet.
        
        Args:
            project_key: Clé du projet SonarQube
            metrics: Liste des métriques à récupérer (ex: ["coverage", "bugs", "code_smells"])
            branch: Nom de la branche (optionnel)
            additional_fields: Champs supplémentaires à inclure dans la réponse
            
        Returns:
            Métriques du projet
            
        Raises:
            ResourceNotFoundError: Si le projet n'existe pas
        """
        endpoint = "measures/component"
        params = {
            "component": project_key,
            "metricKeys": ",".join(metrics)
        }
        
        if branch:
            params["branch"] = branch
        
        if additional_fields:
            params["additionalFields"] = ",".join(additional_fields)
            
        logger.info(f"Fetching metrics for project {project_key} with parameters: {params}")
        
        try:
            response = self.client.get(endpoint, params=params)
            return response
        except ResourceNotFoundError:
            logger.error(f"Project with key '{project_key}' not found")
            raise ResourceNotFoundError(f"Project with key '{project_key}' not found")
            
    def get_project_issues(
        self,
        project_key: str,
        types: Optional[List[str]] = None,  # BUG, VULNERABILITY, CODE_SMELL
        severities: Optional[List[str]] = None,  # INFO, MINOR, MAJOR, CRITICAL, BLOCKER
        statuses: Optional[List[str]] = None,  # OPEN, CONFIRMED, RESOLVED, REOPENED, CLOSED
        resolutions: Optional[List[str]] = None,  # FALSE-POSITIVE, WONTFIX, FIXED, REMOVED
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
        branch: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Récupérer les problèmes (issues) d'un projet.
        
        Args:
            project_key: Clé du projet SonarQube
            types: Types de problèmes (BUG, VULNERABILITY, CODE_SMELL)
            severities: Niveaux de sévérité (INFO, MINOR, MAJOR, CRITICAL, BLOCKER)
            statuses: Statuts des problèmes (OPEN, CONFIRMED, RESOLVED, REOPENED, CLOSED)
            resolutions: Résolutions des problèmes (FALSE-POSITIVE, WONTFIX, FIXED, REMOVED)
            created_after: Filtrer les problèmes créés après cette date (format YYYY-MM-DD)
            created_before: Filtrer les problèmes créés avant cette date (format YYYY-MM-DD)
            branch: Nom de la branche (optionnel)
            
        Returns:
            Liste des problèmes correspondant aux critères
        """
        endpoint = "issues/search"
        params = {
            "componentKeys": project_key,
        }
        
        # Ajouter les paramètres optionnels uniquement s'ils sont spécifiés
        if types:
            params["types"] = ",".join(types)
        if severities:
            params["severities"] = ",".join(severities)
        if statuses:
            params["statuses"] = ",".join(statuses)
        if resolutions:
            params["resolutions"] = ",".join(resolutions)
        if created_after:
            params["createdAfter"] = created_after
        if created_before:
            params["createdBefore"] = created_before
        if branch:
            params["branch"] = branch
            
        logger.info(f"Fetching issues for project {project_key} with parameters: {params}")
        
        response = self.client.get(endpoint, params=params, paginate=True)
        # Si response est une liste, cela signifie que la pagination a été gérée
        # Sinon, extraire les issues de la réponse
        return response if isinstance(response, list) else response.get("issues", [])
        
    def get_project_code_coverage(
        self,
        project_key: str,
        branch: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Récupérer les métriques de couverture de code d'un projet.
        
        Args:
            project_key: Clé du projet SonarQube
            branch: Nom de la branche (optionnel)
            
        Returns:
            Métriques de couverture de code
        """
        # Métriques liées à la couverture de code
        coverage_metrics = [
            "coverage",
            "line_coverage",
            "branch_coverage",
            "uncovered_lines",
            "lines_to_cover",
            "uncovered_conditions",
            "conditions_to_cover",
            "tests",
            "test_success_density",
            "test_failures",
            "test_errors",
            "skipped_tests",
            "test_execution_time",
        ]
        
        return self.get_project_metrics(project_key, coverage_metrics, branch)
        
    def get_project_quality_metrics(
        self,
        project_key: str,
        branch: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Récupérer les métriques de qualité de code d'un projet.
        
        Args:
            project_key: Clé du projet SonarQube
            branch: Nom de la branche (optionnel)
            
        Returns:
            Métriques de qualité de code
        """
        # Métriques liées à la qualité du code
        quality_metrics = [
            "bugs",
            "reliability_rating",
            "vulnerabilities",
            "security_rating",
            "security_hotspots",
            "security_hotspots_reviewed",
            "code_smells",
            "sqale_index",  # Dette technique en minutes
            "sqale_debt_ratio",  # Ratio de dette technique
            "maintainability_rating",
            "duplicated_lines_density",
            "duplicated_blocks",
            "cognitive_complexity",
            "complexity",
        ]
        
        return self.get_project_metrics(project_key, quality_metrics, branch)
        
    def get_project_activity(
        self,
        project_key: str,
        metrics: Optional[List[str]] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        branch: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Récupérer l'historique des analyses et métriques d'un projet.
        
        Args:
            project_key: Clé du projet SonarQube
            metrics: Liste des métriques à récupérer (si None, toutes les métriques disponibles)
            from_date: Date de début au format YYYY-MM-DD
            to_date: Date de fin au format YYYY-MM-DD
            branch: Nom de la branche (optionnel)
            
        Returns:
            Historique des analyses et métriques
        """
        endpoint = "measures/search_history"
        params = {
            "component": project_key,
        }
        
        # Métriques par défaut si non spécifiées
        if not metrics:
            metrics = [
                "bugs", 
                "vulnerabilities", 
                "code_smells", 
                "coverage",
                "duplicated_lines_density"
            ]
            
        params["metrics"] = ",".join(metrics)
        
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        if branch:
            params["branch"] = branch
            
        logger.info(f"Fetching activity history for project {project_key} with parameters: {params}")
        
        response = self.client.get(endpoint, params=params)
        return response
