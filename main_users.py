import os
from dotenv import load_dotenv
from src.extractors.gitlab.gitlab_client_improved import GitLabClient
from src.extractors.gitlab.users_gateway import GitLabUsersGateway
from src.utils import save_json

def fetch_all_users(users_gateway):
    print("\n👥 Extraction de tous les utilisateurs internes GitLab...")
    all_users = users_gateway.get_all_users()
    print(f"[INFO] Nombre d'utilisateurs internes : {len(all_users)}")
    save_json(all_users, "all_users.json")

def main():
    load_dotenv()

    private_token = os.getenv("GITLAB_PRIVATE_TOKEN")
    if not private_token:
        raise ValueError("❌ Le token GitLab est manquant dans le fichier .env.")

    gitlab_api_url = os.getenv("GITLAB_API_URL", "https://gitlab.com").rstrip("/")
    if not gitlab_api_url.endswith("/api/v4"):
        gitlab_api_url += "/api/v4"

    config = {
        "api_url": gitlab_api_url,
        "private_token": private_token,
        "timeout": int(os.getenv("GITLAB_TIMEOUT", 10)),
        "max_retries": int(os.getenv("GITLAB_MAX_RETRIES", 3)),
        "retry_delay": int(os.getenv("GITLAB_RETRY_DELAY", 2)),
        "verify_ssl": os.getenv("GITLAB_VERIFY_SSL", "true").lower() == "true"
    }

    client = GitLabClient(config)
    users_gateway = GitLabUsersGateway(client)

    # Extraction des membres d'un groupe GitLab
    group_id = os.getenv("GITLAB_GROUP_ID")
    if not group_id:
        raise ValueError("❌ L'identifiant du groupe GitLab (GITLAB_GROUP_ID) est manquant dans le fichier .env.")
    print(f"\n👥 Extraction des membres du groupe GitLab {group_id}...")
    group_members = users_gateway.get_group_members(int(group_id))
    print(f"[INFO] Nombre de membres dans le groupe : {len(group_members)}")
    save_json(group_members, "group_members.json")

    # Extraction de tous les utilisateurs internes
    fetch_all_users(users_gateway)

if __name__ == "__main__":
    main()
