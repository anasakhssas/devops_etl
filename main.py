import os
import json
from dotenv import load_dotenv

from src.extractors.gitlab.gitlab_client_improved import GitLabClient
from src.extractors.gitlab.projects_gateway import GitLabProjectsGateway
from src.utils import save_json  # 🔧 Fonction utilitaire pour sauvegarder les données

# ---------------------------
# 📁 FONCTIONS MÉTIERS
# ---------------------------

def fetch_projects(projects_gateway, params=None):
    projects = projects_gateway.get_projects(params=params)
    print(f"[DEBUG] Nombre de projets extraits : {len(projects)}")
    return projects

def fetch_project_commits(projects_gateway, project_id, params=None):
    commits = projects_gateway.get_project_commits(project_id, params=params)
    print(f"[DEBUG] Nombre de commits extraits pour le projet {project_id} : {len(commits)}")
    return commits

def test_get_project_commits(projects_gateway, project_id):
    print(f"\n[TEST] Commits du projet ID: {project_id}")
    commits = projects_gateway.get_project_commits(project_id)
    print(f"[TEST] Nombre de commits récupérés: {len(commits)}")
    for i, commit in enumerate(commits[:3], start=1):
        print(f"   {i}. {commit.get('short_id')} - {commit.get('title', commit.get('message', '')).splitlines()[0]}")
    if len(commits) > 3:
        print(f"   ...et {len(commits)-3} autres commits.")

def fetch_all_projects_and_commits(projects_gateway, params=None):
    projects = projects_gateway.get_projects(params=params)
    print(f"[DEBUG] Nombre de projets extraits : {len(projects)}")

    all_data = {}
    for i, project in enumerate(projects, start=1):
        project_id = project['id']
        print(f"\n[{i}] 📁 {project['name']} (ID: {project_id})")
        commits = projects_gateway.get_project_commits(project_id)
        print(f"   Nombre de commits: {len(commits)}")
        all_data[project_id] = {"project": project, "commits": commits}
    return all_data

def fetch_projects_commits_count(projects_gateway, params=None):
    projects = projects_gateway.get_projects(params=params)
    result = {}
    for project in projects:
        commits = projects_gateway.get_project_commits(project['id'])
        result[project['name']] = len(commits)
    return result

def test_projects_gateway_methods(projects_gateway, params=None):
    result = {}
    projects = projects_gateway.get_projects(params=params)
    if not projects:
        print("Aucun projet trouvé pour les tests.")
        return {}

    first_project = projects[0]
    pid = first_project['id']
    pname = first_project['name']
    result['project_tested'] = {"id": pid, "name": pname}

    try: result['get_projects'] = {"count": len(projects)}
    except Exception as e: result['get_projects'] = {"error": str(e)}
    try: result['get_project_members'] = {"count": len(projects_gateway.get_project_members(pid))}
    except Exception as e: result['get_project_members'] = {"error": str(e)}
    try: result['get_project_commits'] = {"count": len(projects_gateway.get_project_commits(pid))}
    except Exception as e: result['get_project_commits'] = {"error": str(e)}
    try: result['get_project_merge_requests'] = {"count": len(projects_gateway.get_project_merge_requests(pid))}
    except Exception as e: result['get_project_merge_requests'] = {"error": str(e)}
    try: result['get_project_issues'] = {"count": len(projects_gateway.get_project_issues(pid))}
    except Exception as e: result['get_project_issues'] = {"error": str(e)}
    try: result['get_project_pipelines'] = {"count": len(projects_gateway.get_project_pipelines(pid))}
    except Exception as e: result['get_project_pipelines'] = {"error": str(e)}
    try: result['get_project_branches'] = {"count": len(projects_gateway.get_project_branches(pid))}
    except Exception as e: result['get_project_branches'] = {"error": str(e)}

    return result

# ---------------------------
# 🚀 MAIN
# ---------------------------

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
    projects_gateway = GitLabProjectsGateway(client)

    # 📥 Étape 1 : Projets
    print("\n📂 Récupération des projets...")
    projects = fetch_projects(projects_gateway, params={"membership": True})
    save_json(projects, "projects.json")

    # 📊 Étape 2 : Nombre de commits par projet
    print("\n📈 Comptage des commits par projet...")
    commits_count = fetch_projects_commits_count(projects_gateway, params={"membership": True})
    save_json(commits_count, "commits_count.json")

    # 🧪 Étape 3 : Test complet des méthodes de ProjectsGateway
    print("\n🧪 Tests des méthodes GitLab...")
    tests = test_projects_gateway_methods(projects_gateway, params={"membership": True})
    save_json(tests, "tests_methods.json")

    # 🗃️ Étape 4 : Projets + commits
    print("\n📦 Extraction complète des projets avec leurs commits...")
    all_data = fetch_all_projects_and_commits(projects_gateway, params={"membership": True})
    save_json(all_data, "projects_commits_full.json")

    print("\n✅ Extraction terminée.")

if __name__ == "__main__":
    main()
