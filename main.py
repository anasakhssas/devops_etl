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

def fetch_all_projects_resources(projects_gateway, params=None):
    """
    Récupère pour chaque projet toutes les ressources principales (commits, pipelines, issues, branches, merge requests, membres)
    et retourne un dictionnaire structuré.
    :param projects_gateway: Instance de GitLabProjectsGateway
    :param params: Dictionnaire de paramètres optionnels pour le filtrage des projets
    :return: Dictionnaire {projet_id: {"project": {...}, "commits": [...], "pipelines": [...], "issues": [...], "branches": [...], "merge_requests": [...], "members": [...]}}
    """
    projects = projects_gateway.get_projects(params=params)
    print(f"[DEBUG] Nombre de projets extraits : {len(projects)}")
    all_data = {}
    for i, project in enumerate(projects, start=1):
        project_id = project['id']
        print(f"\n[{i}] 📁 {project['name']} (ID: {project_id})")
        commits = projects_gateway.get_project_commits(project_id)
        pipelines = projects_gateway.get_project_pipelines(project_id)
        issues = projects_gateway.get_project_issues(project_id)
        branches = projects_gateway.get_project_branches(project_id)
        merge_requests = projects_gateway.get_project_merge_requests(project_id)
        members = projects_gateway.get_project_members(project_id)
        all_data[project_id] = {
            "project": project,
            "commits": commits,
            "pipelines": pipelines,
            "issues": issues,
            "branches": branches,
            "merge_requests": merge_requests,
            "members": members
        }
        print(f"   commits: {len(commits)}, pipelines: {len(pipelines)}, issues: {len(issues)}, branches: {len(branches)}, merge_requests: {len(merge_requests)}, members: {len(members)}")
    return all_data

def fetch_all_projects_pipelines(projects_gateway, params=None):
    projects = projects_gateway.get_projects(params=params)
    print(f"[DEBUG] Nombre de projets extraits : {len(projects)}")
    all_pipelines = {}
    for p in projects:
        project_id = p['id']
        project_name = p['name']
        pipelines = projects_gateway.get_project_pipelines(project_id)
        all_pipelines[project_name] = pipelines
        print(f"[DEBUG] {project_name} ({project_id}): {len(pipelines)} pipelines")
    return all_pipelines

def fetch_all_projects_issues(projects_gateway, params=None):
    projects = projects_gateway.get_projects(params=params)
    print(f"[DEBUG] Nombre de projets extraits : {len(projects)}")
    all_issues = {}
    for p in projects:
        project_id = p['id']
        project_name = p['name']
        issues = projects_gateway.get_project_issues(project_id)
        all_issues[project_name] = issues
        print(f"[DEBUG] {project_name} ({project_id}): {len(issues)} issues")
    return all_issues

def fetch_all_projects_branches(projects_gateway, params=None):
    projects = projects_gateway.get_projects(params=params)
    print(f"[DEBUG] Nombre de projets extraits : {len(projects)}")
    all_branches = {}
    for p in projects:
        project_id = p['id']
        project_name = p['name']
        branches = projects_gateway.get_project_branches(project_id)
        all_branches[project_name] = branches
        print(f"[DEBUG] {project_name} ({project_id}): {len(branches)} branches")
    return all_branches

def fetch_all_projects_merge_requests(projects_gateway, params=None):
    projects = projects_gateway.get_projects(params=params)
    print(f"[DEBUG] Nombre de projets extraits : {len(projects)}")
    all_mrs = {}
    for p in projects:
        project_id = p['id']
        project_name = p['name']
        mrs = projects_gateway.get_project_merge_requests(project_id)
        all_mrs[project_name] = mrs
        print(f"[DEBUG] {project_name} ({project_id}): {len(mrs)} merge requests")
    return all_mrs

def fetch_all_projects_members(projects_gateway, params=None):
    projects = projects_gateway.get_projects(params=params)
    print(f"[DEBUG] Nombre de projets extraits : {len(projects)}")
    all_members = {}
    for p in projects:
        project_id = p['id']
        project_name = p['name']
        members = projects_gateway.get_project_members(project_id)
        all_members[project_name] = members
        print(f"[DEBUG] {project_name} ({project_id}): {len(members)} members")
    return all_members

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

    # 📄 Étape 3 : Commits complets par projet
    print("\n📄 Extraction des commits complets par projet...")
    all_commits = fetch_all_projects_and_commits(projects_gateway, params={"membership": True})
    save_json(all_commits, "projects_commits_full.json")

    # 🧪 Étape 4 : Test complet des méthodes de ProjectsGateway
    print("\n🧪 Tests des méthodes GitLab...")
    tests = test_projects_gateway_methods(projects_gateway, params={"membership": True})
    save_json(tests, "tests_methods.json")

    # 🗃️ Étape 5 : Pipelines par projet
    print("\n🗃️ Extraction des pipelines par projet...")
    all_pipelines = fetch_all_projects_pipelines(projects_gateway, params={"membership": True})
    save_json(all_pipelines, "projects_pipelines_full.json")

    # 🗃️ Étape 6 : Issues par projet
    print("\n🗃️ Extraction des issues par projet...")
    all_issues = fetch_all_projects_issues(projects_gateway, params={"membership": True})
    save_json(all_issues, "projects_issues_full.json")

    # 🗃️ Étape 7 : Branches par projet
    print("\n🗃️ Extraction des branches par projet...")
    all_branches = fetch_all_projects_branches(projects_gateway, params={"membership": True})
    save_json(all_branches, "projects_branches_full.json")

    # 🗃️ Étape 8 : Merge Requests par projet
    print("\n🗃️ Extraction des merge requests par projet...")
    all_mrs = fetch_all_projects_merge_requests(projects_gateway, params={"membership": True})
    save_json(all_mrs, "projects_merge_requests_full.json")

    # 🗃️ Étape 9 : Membres par projet
    print("\n🗃️ Extraction des membres par projet...")
    all_members = fetch_all_projects_members(projects_gateway, params={"membership": True})
    save_json(all_members, "projects_members_full.json")

    print("\n✅ Extraction terminée.")

if __name__ == "__main__":
    main()
