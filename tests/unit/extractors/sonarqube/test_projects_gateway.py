"""
Module de tests unitaires pour SonarQubeProjectsGateway.

Ce module contient les tests pour la classe SonarQubeProjectsGateway qui gère
l'interaction avec les projets et les métriques SonarQube.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.core.exceptions import ResourceNotFoundError
from src.extractors.sonarqube.projects_gateway import SonarQubeProjectsGateway
from src.extractors.sonarqube.sonarqube_client import SonarQubeClient


class TestSonarQubeProjectsGateway:
    """Tests pour la classe SonarQubeProjectsGateway."""

    @pytest.fixture
    def mock_client(self):
        """Fixture pour créer un mock du client SonarQube."""
        mock = MagicMock(spec=SonarQubeClient)
        return mock

    @pytest.fixture
    def gateway(self, mock_client):
        """Fixture pour créer une instance de SonarQubeProjectsGateway pour les tests."""
        return SonarQubeProjectsGateway(mock_client)

    def test_init(self, mock_client):
        """Tester l'initialisation de la passerelle de projets SonarQube."""
        gateway = SonarQubeProjectsGateway(mock_client)
        assert gateway.client == mock_client

    def test_get_projects_default_params(self, gateway, mock_client):
        """Tester la récupération de projets avec les paramètres par défaut."""
        # Configuration du mock pour simuler une réponse
        mock_client.get.return_value = [{"key": "project1", "name": "Project 1"}]
        
        result = gateway.get_projects()
        
        # Vérifier que la méthode a appelé l'API avec les bons arguments
        mock_client.get.assert_called_once_with(
            "projects/search",
            params={"qualifiers": "TRK"},
            paginate=True
        )
        
        assert result == [{"key": "project1", "name": "Project 1"}]

    def test_get_projects_with_parameters(self, gateway, mock_client):
        """Tester la récupération de projets avec des paramètres personnalisés."""
        # Configuration du mock pour simuler une réponse
        mock_client.get.return_value = [{"key": "project1", "name": "Project 1"}]
        
        result = gateway.get_projects(
            organization="my-org",
            q="test",
            analyzed_after="2023-01-01",
            project_keys=["project1", "project2"]
        )
        
        # Vérifier que la méthode a appelé l'API avec les bons arguments
        mock_client.get.assert_called_once_with(
            "projects/search",
            params={
                "qualifiers": "TRK",
                "organization": "my-org",
                "q": "test",
                "analyzedAfter": "2023-01-01",
                "projects": "project1,project2"
            },
            paginate=True
        )

    def test_get_project_success(self, gateway, mock_client):
        """Tester la récupération d'un projet spécifique avec succès."""
        # Configuration du mock pour simuler une réponse
        mock_response = {"component": {"key": "project1", "name": "Project 1"}}
        mock_client.get.return_value = mock_response
        
        result = gateway.get_project("project1")
        
        # Vérifier que la méthode a appelé l'API avec les bons arguments
        mock_client.get.assert_called_once_with(
            "components/show",
            params={"component": "project1"}
        )
        
        assert result == mock_response

    def test_get_project_not_found(self, gateway, mock_client):
        """Tester la récupération d'un projet inexistant."""
        # Configuration du mock pour simuler une erreur ResourceNotFound
        mock_client.get.side_effect = ResourceNotFoundError("Project with key 'nonexistent' not found")
        
        with pytest.raises(ResourceNotFoundError):
            gateway.get_project("nonexistent")

    def test_get_project_metrics(self, gateway, mock_client):
        """Tester la récupération des métriques d'un projet."""
        # Configuration du mock pour simuler une réponse
        mock_response = {
            "component": {
                "key": "project1",
                "measures": [
                    {"metric": "coverage", "value": "85.5"},
                    {"metric": "bugs", "value": "12"}
                ]
            }
        }
        mock_client.get.return_value = mock_response
        
        result = gateway.get_project_metrics("project1", ["coverage", "bugs"])
        
        # Vérifier que la méthode a appelé l'API avec les bons arguments
        mock_client.get.assert_called_once_with(
            "measures/component",
            params={
                "component": "project1",
                "metricKeys": "coverage,bugs"
            }
        )
        
        assert result == mock_response

    def test_get_project_metrics_with_branch(self, gateway, mock_client):
        """Tester la récupération des métriques d'un projet avec branche spécifiée."""
        # Configuration du mock pour simuler une réponse
        mock_response = {
            "component": {
                "key": "project1",
                "measures": [
                    {"metric": "coverage", "value": "85.5"},
                ]
            }
        }
        mock_client.get.return_value = mock_response
        
        result = gateway.get_project_metrics(
            "project1", 
            ["coverage"], 
            branch="develop",
            additional_fields=["periods"]
        )
        
        # Vérifier que la méthode a appelé l'API avec les bons arguments
        mock_client.get.assert_called_once_with(
            "measures/component",
            params={
                "component": "project1",
                "metricKeys": "coverage",
                "branch": "develop",
                "additionalFields": "periods"
            }
        )
        
        assert result == mock_response

    def test_get_project_issues(self, gateway, mock_client):
        """Tester la récupération des problèmes (issues) d'un projet."""
        # Configuration du mock pour simuler une réponse
        mock_response = [
            {"key": "issue1", "severity": "MAJOR", "type": "BUG"},
            {"key": "issue2", "severity": "MINOR", "type": "CODE_SMELL"}
        ]
        mock_client.get.return_value = mock_response
        
        result = gateway.get_project_issues(
            "project1",
            types=["BUG", "CODE_SMELL"],
            severities=["MAJOR", "MINOR"],
            statuses=["OPEN"],
            created_after="2023-01-01"
        )
        
        # Vérifier que la méthode a appelé l'API avec les bons arguments
        mock_client.get.assert_called_once_with(
            "issues/search",
            params={
                "componentKeys": "project1",
                "types": "BUG,CODE_SMELL",
                "severities": "MAJOR,MINOR",
                "statuses": "OPEN",
                "createdAfter": "2023-01-01"
            },
            paginate=True
        )
        
        assert result == mock_response

    def test_get_project_code_coverage(self, gateway, mock_client):
        """Tester la récupération des métriques de couverture de code."""
        # Configuration du mock pour simuler une réponse
        mock_response = {
            "component": {
                "key": "project1",
                "measures": [
                    {"metric": "coverage", "value": "85.5"},
                    {"metric": "line_coverage", "value": "87.2"}
                ]
            }
        }
        mock_client.get.return_value = mock_response
        
        result = gateway.get_project_code_coverage("project1", branch="main")
        
        # Vérifier que les métriques de couverture sont demandées
        called_args = mock_client.get.call_args
        assert called_args[0][0] == "measures/component"
        assert called_args[1]["params"]["component"] == "project1"
        assert called_args[1]["params"]["branch"] == "main"
        
        # Vérifier que la liste des métriques contient bien les métriques de couverture
        metrics_param = called_args[1]["params"]["metricKeys"].split(",")
        assert "coverage" in metrics_param
        assert "line_coverage" in metrics_param
        assert "tests" in metrics_param
        
        assert result == mock_response

    def test_get_project_quality_metrics(self, gateway, mock_client):
        """Tester la récupération des métriques de qualité."""
        # Configuration du mock pour simuler une réponse
        mock_response = {
            "component": {
                "key": "project1",
                "measures": [
                    {"metric": "bugs", "value": "12"},
                    {"metric": "code_smells", "value": "45"}
                ]
            }
        }
        mock_client.get.return_value = mock_response
        
        result = gateway.get_project_quality_metrics("project1")
        
        # Vérifier que les métriques de qualité sont demandées
        called_args = mock_client.get.call_args
        assert called_args[0][0] == "measures/component"
        assert called_args[1]["params"]["component"] == "project1"
        
        # Vérifier que la liste des métriques contient bien les métriques de qualité
        metrics_param = called_args[1]["params"]["metricKeys"].split(",")
        assert "bugs" in metrics_param
        assert "code_smells" in metrics_param
        assert "reliability_rating" in metrics_param
        
        assert result == mock_response

    def test_get_project_activity(self, gateway, mock_client):
        """Tester la récupération de l'historique des analyses et métriques."""
        # Configuration du mock pour simuler une réponse
        mock_response = {
            "measures": [
                {
                    "metric": "bugs",
                    "history": [
                        {"date": "2023-01-01", "value": "10"},
                        {"date": "2023-01-15", "value": "5"}
                    ]
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        result = gateway.get_project_activity(
            "project1",
            metrics=["bugs"],
            from_date="2023-01-01",
            to_date="2023-01-31"
        )
        
        # Vérifier que la méthode a appelé l'API avec les bons arguments
        mock_client.get.assert_called_once_with(
            "measures/search_history",
            params={
                "component": "project1",
                "metrics": "bugs",
                "from": "2023-01-01",
                "to": "2023-01-31"
            }
        )
        
        assert result == mock_response
