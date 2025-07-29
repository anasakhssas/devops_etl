# main_loading.py

from src.loaders.users_load import load_users
from src.loaders.load_projects import load_projects
from src.loaders.load_commits import load_commits
from src.loaders.load_branches import load_branches
from src.loaders.load_merge_requests import load_merge_requests
from src.loaders.load_pipelines import load_pipelines
from src.loaders.load_issues import load_issues
from src.loaders.load_events import load_events

if __name__ == "__main__":
    print("📥 Chargement des données GitLab dans PostgreSQL...")

    load_users()
    load_projects()
    load_commits()
    load_branches()
    load_merge_requests()
    load_pipelines()
    load_issues()
    load_events()

    print("✅ Tous les chargements sont terminés.")
