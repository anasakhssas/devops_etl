import os
from dotenv import load_dotenv
from src.extractors.gitlab.gitlab_client_improved import GitLabClient
from src.extractors.gitlab.projects_gateway import GitLabProjectsGateway

def fetch_projects(projects_gateway, params=None):
    """
    Récupère les projets GitLab via la passerelle.
    :param projects_gateway: Instance de GitLabProjectsGateway
    :param params: Dictionnaire de paramètres optionnels pour le filtrage
    :return: Liste de projets (dictionnaires)
    """
    return projects_gateway.get_projects(params=params)

def main():
    # 🔄 Charger les variables d'environnement depuis .env
    load_dotenv()

    # Charger la configuration GitLab depuis les variables d'environnement (.env)
    gitlab_api_url = os.getenv("GITLAB_API_URL", "https://gitlab.com").replace("/api/v4", "")
    gitlab_config = {
        "api_url": gitlab_api_url,
        "private_token": os.getenv("GITLAB_PRIVATE_TOKEN")
    }

    # 🛠️ Initialiser le client GitLab amélioré avec la configuration
    client = GitLabClient(gitlab_config)

    # 📂 Utiliser le ProjectsGateway pour récupérer les projets
    projects_gateway = GitLabProjectsGateway(client)
    projects = fetch_projects(projects_gateway)

    if projects:
        print("✅ Projets récupérés avec succès :")
        for i, project in enumerate(projects, start=1):
            print(f"{i}. 📁 {project['name']} - ID: {project['id']}")
    else:
        print("❌ Aucun projet trouvé ou erreur lors de la récupération.")

if __name__ == "__main__":
    main()
