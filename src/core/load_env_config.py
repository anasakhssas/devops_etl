# src/core/load_env_config.py
import os
from dotenv import load_dotenv

def load_gitlab_config_from_env() -> dict:
    load_dotenv()  # charge .env depuis la racine

    return {
        "api_url": os.getenv("GITLAB_API_URL"),
        "private_token": os.getenv("GITLAB_PRIVATE_TOKEN"),
        "timeout": int(os.getenv("GITLAB_TIMEOUT", 10)),
        "max_retries": int(os.getenv("GITLAB_MAX_RETRIES", 3)),
        "retry_delay": int(os.getenv("GITLAB_RETRY_DELAY", 2)),
        "items_per_page": int(os.getenv("GITLAB_ITEMS_PER_PAGE", 100)),
        "verify_ssl": os.getenv("GITLAB_VERIFY_SSL", "true").lower() == "true",
        # optionnel :
        "proxy": {
            "http": os.getenv("HTTP_PROXY"),
            "https": os.getenv("HTTPS_PROXY"),
        }
    }
