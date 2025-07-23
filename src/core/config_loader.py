# src/core/config_loader.py
import os
from dotenv import load_dotenv

load_dotenv()  # charge .env dans os.environ

def load_gitlab_config():
    return {
        "api_url": os.getenv("GITLAB_API_URL"),
        "private_token": os.getenv("GITLAB_PRIVATE_TOKEN"),
        "timeout": int(os.getenv("GITLAB_TIMEOUT", 10)),
        "max_retries": int(os.getenv("GITLAB_MAX_RETRIES", 3)),
        "retry_delay": int(os.getenv("GITLAB_RETRY_DELAY", 2)),
        "items_per_page": int(os.getenv("GITLAB_ITEMS_PER_PAGE", 50)),
        "verify_ssl": os.getenv("GITLAB_VERIFY_SSL", "true").lower() == "true"
    }
