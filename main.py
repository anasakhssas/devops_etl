# main.py

from src.core.config_loader import load_gitlab_config
from src.extractors.gitlab.gitlab_client_improved import GitLabClient

def main():
    config = load_gitlab_config()
    client = GitLabClient(config)

    result = client.test_connection()

    if result["connection_successful"]:
        print("✅ Connexion réussie à GitLab !")
        print("Utilisateur :", result["user_information"]["username"])
        print("Version GitLab :", result["gitlab_version"])
    else:
        print("❌ Connexion échouée :", result.get("error_message"))

if __name__ == "__main__":
    main()
