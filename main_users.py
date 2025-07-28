import os
from dotenv import load_dotenv
from src.extractors.gitlab.gitlab_client_improved import GitLabClient
from src.extractors.gitlab.users_gateway import GitLabUsersGateway
from src.utils import save_json, get_last_extraction_date, set_last_extraction_date
from datetime import datetime

def main():
    load_dotenv()

    # Chargement des variables d'environnement
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

    print("\n👥 Extraction incrémentielle des utilisateurs GitLab...")

    # 🕐 Récupération de la dernière date d'extraction
    last_date = get_last_extraction_date("users")  # data/last_extraction_users.txt
    print(f"[INFO] Dernière date d'extraction connue : {last_date}")

    # 📥 Extraction des utilisateurs mis à jour depuis la dernière extraction
    params = {"active": True}
    if last_date:
        params["updated_after"] = last_date

    users = users_gateway.get_users(params=params)
    print(f"[INFO] Nombre d’utilisateurs récupérés : {len(users)}")

    # 💾 Sauvegarde des données extraites
    save_json(users, "users_incremental.json")

    # 🔄 Mise à jour de la date d’extraction si des utilisateurs sont extraits
        # 🔄 Mise à jour de la date d’extraction si des utilisateurs sont extraits
    if users:
        dates = [u.get("updated_at") for u in users if u.get("updated_at")]
        if dates:
            latest_date = max(dates)
            set_last_extraction_date("users", latest_date)
            print(f"[INFO] Date d'extraction mise à jour : {latest_date}")
        else:
            print("[⚠️] Aucune date 'updated_at' trouvée parmi les utilisateurs.")
    else:
        print("[INFO] Aucune mise à jour utilisateur détectée.")

if __name__ == "__main__":
    main()
