import os
from dotenv import load_dotenv
from src.extractors.gitlab.gitlab_client_improved import GitLabClient
from src.extractors.gitlab.users_gateway import GitLabUsersGateway
from src.utils import save_json, get_last_extraction_date, set_last_extraction_date

def fetch_all_users(users_gateway):
    last_date = get_last_extraction_date("users")
    print("\n👥 Extraction incrémentielle des utilisateurs internes GitLab...")
    all_users = users_gateway.get_all_users()
    # Filtrage manuel par date
    if last_date:
        filtered_users = [
            u for u in all_users
            if (u.get("updated_at") and u["updated_at"] > last_date)
            or (u.get("created_at") and u["created_at"] > last_date)
        ]
    else:
        filtered_users = all_users
    print(f"[INFO] Nombre d'utilisateurs internes extraits : {len(filtered_users)}")
    save_json(filtered_users, "all_users_incremental.json")
    # Mise à jour de la date d'extraction
    if filtered_users:
        dates = [
            u.get("updated_at", u.get("created_at"))
            for u in filtered_users if u.get("updated_at") or u.get("created_at")
        ]
        if dates:
            latest_date = max(dates)
            set_last_extraction_date("users", latest_date)
            print(f"[INFO] Date d'extraction utilisateurs mise à jour : {latest_date}")

def fetch_all_groups(users_gateway):
    last_date = get_last_extraction_date("groups")
    print("\n👥 Extraction incrémentielle des groupes GitLab...")
    all_groups = users_gateway.get_all_groups()
    # Filtrage manuel par date
    if last_date:
        filtered_groups = [
            g for g in all_groups
            if (g.get("updated_at") and g["updated_at"] > last_date)
            or (g.get("created_at") and g["created_at"] > last_date)
        ]
    else:
        filtered_groups = all_groups
    print(f"[INFO] Nombre de groupes extraits : {len(filtered_groups)}")
    save_json(filtered_groups, "all_groups_incremental.json")
    # Mise à jour de la date d'extraction
    if filtered_groups:
        dates = [
            g.get("updated_at", g.get("created_at"))
            for g in filtered_groups if g.get("updated_at") or g.get("created_at")
        ]
        if dates:
            latest_date = max(dates)
            set_last_extraction_date("groups", latest_date)
            print(f"[INFO] Date d'extraction groupes mise à jour : {latest_date}")

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

    # Extraction des membres d'un groupe GitLab (non incrémental)
    group_id = os.getenv("GITLAB_GROUP_ID")
    if not group_id:
        raise ValueError("❌ L'identifiant du groupe GitLab (GITLAB_GROUP_ID) est manquant dans le fichier .env.")
    print(f"\n👥 Extraction des membres du groupe GitLab {group_id}...")
    group_members = users_gateway.get_group_members(int(group_id))
    print(f"[INFO] Nombre de membres dans le groupe : {len(group_members)}")
    save_json(group_members, "group_members.json")

    # Extraction incrémentielle des utilisateurs internes
    fetch_all_users(users_gateway)

    # Extraction incrémentielle des groupes
    fetch_all_groups(users_gateway)

if __name__ == "__main__":
    main()
