import pytest
from src.extractors.gitlab.gitlab_client_improved import GitLabClient
from src.extractors.gitlab.projects_gateway import GitLabProjectsGateway
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

@pytest.fixture(scope="module")
def real_gitlab_client():
    """Fixture avec le vrai client GitLab connecté"""
    config = {
        "api_url": os.getenv("GITLAB_API_URL"),
        "private_token": os.getenv("GITLAB_PRIVATE_TOKEN"),
        "verify_ssl": os.getenv("GITLAB_VERIFY_SSL", "true").lower() == "true"
    }
    client = GitLabClient(config)
    client.connect()
    yield client
    client.close_connection()

@pytest.fixture
def real_gateway(real_gitlab_client):
    """Fixture avec la vraie gateway"""
    return GitLabProjectsGateway(real_gitlab_client)

class TestGitLabProjectsGatewayReal:
    @pytest.mark.integration
    def test_get_projects_basic(self, real_gateway):
        """Test basique de récupération de projets"""
        projects = real_gateway.get_projects({"per_page": 1})
        assert isinstance(projects, list)
        if projects:  # Si on a des projets
            assert "id" in projects[0]
            assert "name" in projects[0]

    @pytest.mark.integration
    def test_get_single_project(self, real_gateway):
        """Test de récupération d'un projet spécifique"""
        # On récupère d'abord un projet existant
        projects = real_gateway.get_projects({"per_page": 1})
        if not projects:
            pytest.skip("Aucun projet disponible pour le test")
        
        project_id = projects[0]["id"]
        project = real_gateway.get_project(project_id)
        
        assert isinstance(project, dict)
        assert project["id"] == project_id
        assert "name" in project

    @pytest.mark.integration
    def test_get_project_members(self, real_gateway):
        """Test de récupération des membres d'un projet"""
        projects = real_gateway.get_projects({"per_page": 1})
        if not projects:
            pytest.skip("Aucun projet disponible pour le test")
        
        members = real_gateway.get_project_members(projects[0]["id"])
        assert isinstance(members, list)
        if members:  # Si le projet a des membres
            assert "id" in members[0]
            assert "name" in members[0]