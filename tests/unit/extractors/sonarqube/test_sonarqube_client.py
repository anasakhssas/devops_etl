"""
Module de tests unitaires pour SonarQubeClient.

Ce module contient les tests pour la classe SonarQubeClient qui gère
l'authentification et les requêtes vers l'API SonarQube.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.core.exceptions import (
    APIAuthenticationError,
    APIRateLimitError,
    ConnectionError,
    ResourceNotFoundError,
)
from src.extractors.sonarqube.sonarqube_client import SonarQubeClient


class TestSonarQubeClient:
    """Tests pour la classe SonarQubeClient."""

    @pytest.fixture
    def client(self):
        """Fixture pour créer une instance de SonarQubeClient pour les tests."""
        return SonarQubeClient(
            api_url="https://sonarqube.example.com/api",
            token="test_token",
            timeout=5,
            max_retries=1,
        )

    @pytest.fixture
    def mock_session(self):
        """Fixture pour créer un mock de la session requests."""
        with patch("requests.Session") as mock_session:
            session_instance = MagicMock()
            mock_session.return_value = session_instance
            yield session_instance

    def test_init(self):
        """Tester l'initialisation du client SonarQube."""
        client = SonarQubeClient(
            api_url="https://sonarqube.example.com/api",
            token="test_token",
        )
        
        assert client.api_url == "https://sonarqube.example.com/api"
        assert client.timeout == 30  # Valeur par défaut
        assert "Authorization" in client.session.headers
        assert client.session.headers["Accept"] == "application/json"

    def test_init_with_username_password(self):
        """Tester l'initialisation du client SonarQube avec username/password."""
        client = SonarQubeClient(
            api_url="https://sonarqube.example.com/api",
            username="test_user",
            password="test_password",
        )
        
        assert client.session.auth == ("test_user", "test_password")
        assert client.session.headers["Accept"] == "application/json"

    def test_test_connection_success(self, client, mock_session):
        """Tester une connexion réussie à SonarQube."""
        # Configuration du mock pour simuler une réponse réussie
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "UP"}
        mock_session.get.return_value = mock_response
        
        result = client.test_connection()
        
        # Vérifier que la méthode a appelé l'API avec les bons arguments
        mock_session.get.assert_called_once_with(
            "https://sonarqube.example.com/api/system/status",
            timeout=5
        )
        
        assert result is True

    def test_test_connection_authentication_error(self, client, mock_session):
        """Tester une erreur d'authentification lors de la connexion à SonarQube."""
        # Configuration du mock pour simuler une réponse d'erreur d'authentification
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_session.get.return_value = mock_response
        
        with pytest.raises(APIAuthenticationError):
            client.test_connection()

    def test_test_connection_error(self, client, mock_session):
        """Tester une erreur de connexion à SonarQube."""
        # Configuration du mock pour simuler une erreur de connexion
        mock_session.get.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        with pytest.raises(ConnectionError):
            client.test_connection()

    def test_get_success(self, client, mock_session):
        """Tester une requête GET réussie."""
        # Configuration du mock pour simuler une réponse réussie
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}
        mock_session.request.return_value = mock_response
        
        result = client.get("projects", params={"key": "test"})
        
        # Vérifier que la méthode a appelé l'API avec les bons arguments
        mock_session.request.assert_called_once_with(
            method="GET",
            url="https://sonarqube.example.com/api/projects",
            params={"key": "test"},
            json=None,
            timeout=5
        )
        
        assert result == {"key": "value"}

    def test_get_not_found(self, client, mock_session):
        """Tester une requête GET pour une ressource non trouvée."""
        # Configuration du mock pour simuler une réponse 404
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_session.request.return_value = mock_response
        
        with pytest.raises(ResourceNotFoundError):
            client.get("nonexistent")

    def test_get_rate_limit(self, client, mock_session):
        """Tester une requête GET qui atteint la limite de taux."""
        # Configuration du mock pour simuler une réponse 429
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_session.request.return_value = mock_response
        
        with pytest.raises(APIRateLimitError):
            client.get("projects")

    def test_get_server_error(self, client, mock_session):
        """Tester une requête GET avec une erreur serveur."""
        # Configuration du mock pour simuler une réponse 500
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Server Error")
        mock_session.request.return_value = mock_response
        
        with pytest.raises(ConnectionError):
            client.get("projects")

    def test_paginated_get(self, client, mock_session):
        """Tester la récupération paginée de résultats."""
        # Première page
        first_response = MagicMock()
        first_response.status_code = 200
        first_response.json.return_value = {
            "paging": {
                "pageIndex": 1,
                "pageSize": 2,
                "total": 3
            },
            "components": [{"key": "project1"}, {"key": "project2"}]
        }
        
        # Deuxième page
        second_response = MagicMock()
        second_response.status_code = 200
        second_response.json.return_value = {
            "paging": {
                "pageIndex": 2,
                "pageSize": 2,
                "total": 3
            },
            "components": [{"key": "project3"}]
        }
        
        # Configurer le mock pour retourner différentes réponses selon les paramètres
        def mock_request(*args, **kwargs):
            if kwargs.get("params", {}).get("p") == 1:
                return first_response
            else:
                return second_response
        
        mock_session.request.side_effect = mock_request
        
        # Appeler la méthode avec pagination
        result = client.get("projects/search", params={}, paginate=True)
        
        # Vérifier les résultats
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]["key"] == "project1"
        assert result[1]["key"] == "project2"
        assert result[2]["key"] == "project3"
        
        # Vérifier que la méthode a été appelée deux fois avec les bons paramètres de pagination
        assert mock_session.request.call_count == 2
