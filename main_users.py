import os
import json
from dotenv import load_dotenv

from src.extractors.gitlab.gitlab_client_improved import GitLabClient
from src.extractors.gitlab.users_gateway import GitLabUsersGateway
from src.utils import save_json

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

    # Récupère uniquement TES infos
    print("\n👤 Infos utilisateur courant :")
    user = users_gateway.get_current_user()
    print(json.dumps(user, indent=2, ensure_ascii=False))
    save_json(user, "current_user.json")

    user_id = user.get("id")
    if user_id:
        print("\n👥 Tes groupes :")
        groups = users_gateway.get_user_groups(user_id)
        print(json.dumps(groups, indent=2, ensure_ascii=False))
        save_json(groups, "my_groups.json")

        print("\n📅 Tes events :")
        events = users_gateway.get_user_events(user_id)
        print(json.dumps(events, indent=2, ensure_ascii=False))
        save_json(events, "my_events.json")

    print("\n✅ Extraction terminée.")

if __name__ == "__main__":
    main()