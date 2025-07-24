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
    "api_url": os.getenv("GITLAB_API_URL", "https://gitlab.com"),
    "private_token": os.getenv("GITLAB_PRIVATE_TOKEN"),
    "timeout": int(os.getenv("GITLAB_TIMEOUT", "30")),
    "max_retries": int(os.getenv("GITLAB_MAX_RETRIES", "3")),
    "retry_delay": int(os.getenv("GITLAB_RETRY_DELAY", "5")),
    "items_per_page": int(os.getenv("GITLAB_ITEMS_PER_PAGE", "100")),
    "verify_ssl": os.getenv("GITLAB_VERIFY_SSL", "true").lower() == "true"
}

TEST_PROJECT_ID = os.getenv("TEST_PROJECT_ID")

# --- MOCKED TESTS (ne font pas de vrais appels à GitLab) ---

@pytest.fixture
def gitlab_client() -> GitLabClient:
    """Fixture mockée pour les tests unitaires."""
    config = {
        "api_url": "https://gitlab.com",
        "private_token": "glpat-testtoken",
        "verify_ssl": False
    }
    client = GitLabClient(config)
    # Mock de l'authentification
    with patch.object(client, '_authenticate_user', return_value=True):
        client._current_user_info = {"username": "mockuser"}
        client.establish_connection()
    return client


@pytest.fixture
def projects_gateway(gitlab_client: GitLabClient) -> GitLabProjectsGateway:
    """Passerelle mockée pour tests unitaires."""
    return GitLabProjectsGateway(gitlab_client)

@pytest.mark.skip(reason="Ce test fait un vrai appel API et nécessite un token valide. Utilise test_mock_get_projects pour unitaire.")
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

@pytest.fixture
def real_gitlab_client() -> GitLabClient:
    """Client réel pour tests d'intégration (utilise .env)."""
    client = GitLabClient(GITLAB_CONFIG)
    client.establish_connection()
    return client

@pytest.fixture
def real_projects_gateway(real_gitlab_client: GitLabClient) -> GitLabProjectsGateway:
    """Passerelle réelle pour tests d'intégration."""
    return GitLabProjectsGateway(real_gitlab_client)

def test_real_get_projects(real_projects_gateway: GitLabProjectsGateway):
    """Test réel : récupération des projets sur GitLab."""
    projects = real_projects_gateway.get_projects(params={"membership": True})
    assert isinstance(projects, list)
    print(f"\n[REAL] Projets trouvés: {len(projects)}")
    if projects:
        assert "id" in projects[0]
        # Affiche la liste complète des projets récupérés
        for project in projects:
            print(project)

@pytest.mark.skipif(not TEST_PROJECT_ID, reason="TEST_PROJECT_ID non défini dans .env")
def test_real_get_commits(real_projects_gateway: GitLabProjectsGateway):
    """Test réel : récupération des commits d'un projet."""
    commits = real_projects_gateway.get_project_commits(int(TEST_PROJECT_ID))
    assert isinstance(commits, list)
    print(f"\n[REAL] Commits trouvés: {len(commits)}")
    if commits:
        assert "id" in commits[0]
        # Affiche la liste complète des commits récupérés
        for commit in commits:
            print(commit)

@pytest.mark.skipif(not TEST_PROJECT_ID, reason="TEST_PROJECT_ID non défini dans .env")
def test_real_get_pipelines(real_projects_gateway: GitLabProjectsGateway):
    """Test réel : récupération des pipelines d'un projet."""
    pipelines = real_projects_gateway.get_project_pipelines(int(TEST_PROJECT_ID))
    assert isinstance(pipelines, list)
    print(f"\n[REAL] Pipelines trouvés: {len(pipelines)}")
    if pipelines:
        assert "id" in pipelines[0]
        # Affiche la liste complète des pipelines récupérés
        for pipeline in pipelines:
            print(pipeline)

@pytest.mark.skipif(not TEST_PROJECT_ID, reason="TEST_PROJECT_ID non défini dans .env")
def test_real_get_issues(real_projects_gateway: GitLabProjectsGateway):
    """Test réel : récupération des issues d'un projet."""
    issues = real_projects_gateway.get_project_issues(int(TEST_PROJECT_ID))
    assert isinstance(issues, list)
    print(f"\n[REAL] Issues trouvées: {len(issues)}")
    if issues:
        assert "id" in issues[0]
        # Affiche la liste complète des issues récupérées
        for issue in issues:
            print(issue)

@pytest.mark.skipif(not TEST_PROJECT_ID, reason="TEST_PROJECT_ID non défini dans .env")
def test_real_get_merge_requests(real_projects_gateway: GitLabProjectsGateway):
    """Test réel : récupération des merge requests d'un projet."""
    mrs = real_projects_gateway.get_project_merge_requests(int(TEST_PROJECT_ID))
    assert isinstance(mrs, list)
    print(f"\n[REAL] Merge Requests trouvées: {len(mrs)}")
    if mrs:
        assert "id" in mrs[0]
        # Affiche la liste complète des merge requests récupérées
        for mr in mrs:
            print(mr)

@pytest.mark.skipif(not TEST_PROJECT_ID, reason="TEST_PROJECT_ID non défini dans .env")
def test_real_get_branches(real_projects_gateway: GitLabProjectsGateway):
    """Test réel : récupération des branches d'un projet."""
    branches = real_projects_gateway.get_project_branches(int(TEST_PROJECT_ID))
    assert isinstance(branches, list)
    print(f"\n[REAL] Branches trouvées: {len(branches)}")
    if branches:
        assert "name" in branches[0]
        # Affiche la liste complète des branches récupérées
        for branch in branches:
            print(branch)