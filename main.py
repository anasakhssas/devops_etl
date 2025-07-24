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
    projects = projects_gateway.get_projects(params=params)

    print(f"[DEBUG] Nombre de projets extraits : {len(projects)}")
    return projects
def main():
    # Charger les variables d'environnement
    load_dotenv()

    private_token = os.getenv("GITLAB_PRIVATE_TOKEN")
    if not private_token:
        raise ValueError("⚠️ Le token privé GitLab (GITLAB_PRIVATE_TOKEN) est manquant dans le fichier .env.")

    gitlab_api_url = os.getenv("GITLAB_API_URL", "https://gitlab.com").rstrip("/")
    if not gitlab_api_url.endswith("/api/v4"):
        gitlab_api_url += "/api/v4"

    gitlab_config = {
        "api_url": gitlab_api_url,
        "private_token": private_token,
        "timeout": int(os.getenv("GITLAB_TIMEOUT", 10)),
        "max_retries": int(os.getenv("GITLAB_MAX_RETRIES", 3)),
        "retry_delay": int(os.getenv("GITLAB_RETRY_DELAY", 2)),
        "verify_ssl": os.getenv("GITLAB_VERIFY_SSL", "true").lower() == "true"
    }

    # Initialiser client GitLab
    client = GitLabClient(gitlab_config)

    # Créer l'objet gateway avant de l'utiliser
    projects_gateway = GitLabProjectsGateway(client)

    # Maintenant récupérer les projets (par exemple avec filtre membership)
    projects = fetch_projects(projects_gateway, params={"membership": True})

    if projects:
        print("✅ Projets récupérés avec succès :")
        for i, project in enumerate(projects, start=1):
            print(f"{i}. 📁 {project['name']} - ID: {project['id']}")
    else:
        print("❌ Aucun projet trouvé ou erreur lors de la récupération.")


if __name__ == "__main__":
    main()
