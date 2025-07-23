"""
Tests unitaires pour GitLabUsersGateway.

Ce module contient les tests pour la classe GitLabUsersGateway qui
permet d'interagir avec les utilisateurs GitLab via le client harmonisé.
"""

import json
import pytest
from unittest.mock import MagicMock, patch, call

from src.extractors.gitlab.gitlab_client import GitLabClient
from src.extractors.gitlab.users_gateway import GitLabUsersGateway


class TestGitLabUsersGateway:
    """Tests pour la classe GitLabUsersGateway."""

    @pytest.fixture
    def mock_gitlab_client(self):
        """Fixture pour créer un mock de GitLabClient."""
        mock_client = MagicMock(spec=GitLabClient)
        mock_client.is_connected = True
        return mock_client

    @pytest.fixture
    def users_gateway(self, mock_gitlab_client):
        """Fixture pour créer un gateway utilisateurs avec un client mocké."""
        return GitLabUsersGateway(mock_gitlab_client)

    def test_get_users_without_params(self, users_gateway, mock_gitlab_client):
        """Teste la récupération des utilisateurs sans paramètres."""
        # Configuration du mock
        mock_users = [{"id": 1, "username": "user1"}, {"id": 2, "username": "user2"}]
        mock_gitlab_client.api_get.return_value = mock_users

        # Appel de la méthode à tester
        result = users_gateway.get_users()

        # Vérifications
        assert result == mock_users
        mock_gitlab_client.api_get.assert_called_once_with("users", {})

    def test_get_users_with_params(self, users_gateway, mock_gitlab_client):
        """Teste la récupération des utilisateurs avec paramètres."""
        # Configuration du mock
        mock_users = [{"id": 1, "username": "user1"}]
        mock_gitlab_client.api_get.return_value = mock_users
        
        # Paramètres de recherche
        search_params = {"active": "true", "search": "user1"}

        # Appel de la méthode à tester
        result = users_gateway.get_users(search_params)

        # Vérifications
        assert result == mock_users
        mock_gitlab_client.api_get.assert_called_once_with("users", search_params)

    def test_get_user_by_id(self, users_gateway, mock_gitlab_client):
        """Teste la récupération d'un utilisateur par son ID."""
        # Configuration du mock
        mock_user = {"id": 123, "username": "testuser"}
        mock_gitlab_client.api_get.return_value = mock_user

        # Appel de la méthode à tester
        result = users_gateway.get_user_by_id(123)

        # Vérifications
        assert result == mock_user
        mock_gitlab_client.api_get.assert_called_once_with("users/123", {})

    def test_get_user_by_username(self, users_gateway, mock_gitlab_client):
        """Teste la récupération d'un utilisateur par son nom d'utilisateur."""
        # Configuration du mock
        mock_users = [{"id": 456, "username": "specific_user"}]
        mock_gitlab_client.api_get.return_value = mock_users

        # Appel de la méthode à tester
        result = users_gateway.get_user_by_username("specific_user")

        # Vérifications
        assert result == mock_users[0]
        mock_gitlab_client.api_get.assert_called_once_with("users", {"username": "specific_user"})

    def test_get_user_by_username_not_found(self, users_gateway, mock_gitlab_client):
        """Teste le comportement lorsqu'un utilisateur n'est pas trouvé par nom d'utilisateur."""
        # Configuration du mock pour retourner une liste vide (utilisateur non trouvé)
        mock_gitlab_client.api_get.return_value = []

        # Appel de la méthode à tester
        result = users_gateway.get_user_by_username("nonexistent")

        # Vérifications
        assert result is None
        mock_gitlab_client.api_get.assert_called_once_with("users", {"username": "nonexistent"})

    def test_get_current_user(self, users_gateway, mock_gitlab_client):
        """Teste la récupération de l'utilisateur courant."""
        # Configuration du mock
        mock_current_user = {"id": 789, "username": "current_user"}
        mock_gitlab_client.api_get.return_value = mock_current_user

        # Appel de la méthode à tester
        result = users_gateway.get_current_user()

        # Vérifications
        assert result == mock_current_user
        mock_gitlab_client.api_get.assert_called_once_with("user", {})
