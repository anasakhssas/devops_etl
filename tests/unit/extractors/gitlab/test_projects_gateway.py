"""
Module de test pour GitLabProjectsGateway - Version corrigée
"""
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest
from dotenv import load_dotenv

from src.extractors.gitlab.gitlab_client_improved import GitLabClient
from src.extractors.gitlab.projects_gateway import GitLabProjectsGateway

# Charge les variables d'environnement
load_dotenv()

# Configuration
GITLAB_CONFIG = {
    "api_url": os.getenv("GITLAB_API_URL"),
    "private_token": os.getenv("GITLAB_PRIVATE_TOKEN"),
    "timeout": int(os.getenv("GITLAB_TIMEOUT", "30")),
    "max_retries": int(os.getenv("GITLAB_MAX_RETRIES", "3")),
    "retry_delay": int(os.getenv("GITLAB_RETRY_DELAY", "5")),
    "items_per_page": int(os.getenv("GITLAB_ITEMS_PER_PAGE", "100")),
    "verify_ssl": os.getenv("GITLAB_VERIFY_SSL", "true").lower() == "true"
}

TEST_PROJECT_ID = os.getenv("TEST_PROJECT_ID")

@pytest.fixture
def gitlab_client() -> GitLabClient:
    """Fixture pour initialiser le client GitLab."""
    client = GitLabClient(GITLAB_CONFIG)
    client.establish_connection()
    return client

@pytest.fixture
def projects_gateway(gitlab_client: GitLabClient) -> GitLabProjectsGateway:
    """Fixture pour initialiser la passerelle des projets."""
    return GitLabProjectsGateway(gitlab_client)

def test_get_projects(projects_gateway: GitLabProjectsGateway) -> None:
    """Teste la récupération des projets."""
    projects = projects_gateway.get_projects(params={"membership": True})
    assert isinstance(projects, list)
    if projects:
        assert "id" in projects[0]
        print(f"\nProjets trouvés: {len(projects)}")

# ... (autres tests restent identiques mais utiliseront maintenant la bonne méthode)

@patch('src.extractors.gitlab.gitlab_client_improved.GitLabClient')
def test_mock_get_projects(mock_client):
    """Test mocké de get_projects."""
    mock_client_instance = mock_client.return_value
    mock_client_instance.extract_gitlab_resource.return_value = [{"id": 1, "name": "Projet Test"}]
    
    # 1. Test sans paramètres
    gateway = GitLabProjectsGateway(mock_client_instance)
    result = gateway.get_projects()
    
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == 1
    mock_client_instance.extract_gitlab_resource.assert_called_with(
        resource_type="projects",
        additional_parameters={}
    )
    
    # Reset le mock pour le deuxième test
    mock_client_instance.reset_mock()
    mock_client_instance.extract_gitlab_resource.return_value = [{"id": 2, "name": "Projet avec membres"}]
    
    # 2. Test avec paramètres
    result_with_params = gateway.get_projects(params={"membership": True})
    assert len(result_with_params) == 1
    mock_client_instance.extract_gitlab_resource.assert_called_with(
        resource_type="projects",
        additional_parameters={"membership": True}
    )