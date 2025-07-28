import os
import json
from dotenv import load_dotenv
from datetime import datetime
from dateutil.parser import parse as parse_date  # Ajout pour gestion robuste des dates

# --- Ajout: gestion de la date d'extraction incrémentielle ---
LAST_EXTRACTION_FILE = "data/last_extraction_commits.txt"

def get_last_extraction_date(resource_name):
    """
    Récupère la dernière date d'extraction pour une ressource (ex: 'commits').
    Retourne une chaîne ISO 8601 ou None si non trouvée.
    """
    path = LAST_EXTRACTION_FILE
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            date_str = f.read().strip()
            return date_str if date_str else None
    return None

def set_last_extraction_date(resource_name, date_str):
    """
    Sauvegarde la dernière date d'extraction pour une ressource.
    """
    os.makedirs(os.path.dirname(LAST_EXTRACTION_FILE), exist_ok=True)
    with open(LAST_EXTRACTION_FILE, "w", encoding="utf-8") as f:
        f.write(date_str)

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


def fetch_all_projects_branches_incremental(projects_gateway, params=None):
    """
    Extraction incrémentielle des branches basée sur la date du commit de la branche.
    Seules les branches dont le commit est postérieur à la dernière extraction sont retournées.
    """
    last_date = get_last_extraction_date("branches")
    projects = projects_gateway.get_projects(params={"membership": True})
    all_new_branches = {}
    max_commit_date = last_date

    for p in projects:
        project_id = p.get("id")
        branches = projects_gateway.get_project_branches(project_id, params=params)
        new_branches = []
        for branch in branches:
            commit_date = branch.get("commit", {}).get("committed_date")
            if not commit_date:
                continue
            # Si on a une date de dernière extraction, on filtre
            if last_date:
                if commit_date > last_date:
                    new_branches.append(branch)
            else:
                # Première extraction incrémentielle : on prend tout
                new_branches.append(branch)
            # Mise à jour de la date max
            if not max_commit_date or commit_date > max_commit_date:
                max_commit_date = commit_date
        if new_branches:
            all_new_branches[project_id] = new_branches

    print(f"[DEBUG] branches last_date: {last_date}, max_commit_date: {max_commit_date}")
    # Met à jour la date de dernière extraction si de nouvelles branches
    if max_commit_date and max_commit_date != last_date:
        set_last_extraction_date("branches", max_commit_date)
        print(f"[INFO] Date de dernière extraction branches mise à jour: {max_commit_date}")
    else:
        print(f"[INFO] Aucune nouvelle date à enregistrer pour branches.")

    return all_new_branches

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

def fetch_all_projects_commits_incremental(projects_gateway, params=None):
    last_date = get_last_extraction_date("commits")  # format ISO 8601
    projects = projects_gateway.get_projects(params={"membership": True})
    all_commits = {}
    max_commit_date = last_date
    for p in projects:
        project_id = p.get("id")
        commits = projects_gateway.get_project_commits(project_id, params=params)
        new_commits = []
        for commit in commits:
            commit_date = commit.get("created_at") or commit.get("committed_date")
            if not commit_date:
                continue
            # Filtrer explicitement côté Python
            if last_date:
                if commit_date > last_date:
                    new_commits.append(commit)
            else:
                new_commits.append(commit)
            if not max_commit_date or commit_date > max_commit_date:
                max_commit_date = commit_date
        all_commits[project_id] = new_commits
    print(f"[DEBUG] last_date: {last_date}, max_commit_date: {max_commit_date}")
    if max_commit_date and max_commit_date != last_date:
        set_last_extraction_date("commits", max_commit_date)
        print(f"[INFO] Date de dernière extraction mise à jour: {max_commit_date}")
    else:
        print("[INFO] Aucune nouvelle date à enregistrer.")
    return all_commits

# --- Ajout: gestion de la date d'extraction incrémentielle généralisée ---
def get_last_extraction_date(resource_name):
    """
    Récupère la dernière date d'extraction pour une ressource (ex: 'commits', 'issues', 'merge_requests', etc.).
    Retourne une chaîne ISO 8601 ou None si non trouvée.
    """
    path = f"data/last_extraction_{resource_name}.txt"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            date_str = f.read().strip()
            return date_str if date_str else None
    return None

def set_last_extraction_date(resource_name, date_str):
    """
    Sauvegarde la dernière date d'extraction pour une ressource.
    """
    path = f"data/last_extraction_{resource_name}.txt"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(date_str)

def fetch_all_projects_resource_incremental(projects_gateway, resource, params=None, date_field="updated_at", api_param="updated_after"):
    """
    Extraction incrémentielle générique pour une ressource projet (issues, merge_requests, pipelines...).
    Seuls les éléments dont la date (date_field) est postérieure à la dernière extraction sont retournés.
    """
    last_date = get_last_extraction_date(resource)
    projects = projects_gateway.get_projects(params={"membership": True})
    all_items = {}
    max_date = last_date
    for p in projects:
        project_id = p.get("id")
        if resource == "merge_requests":
            items = projects_gateway.get_project_merge_requests(project_id, params=params)
        elif resource == "issues":
            items = projects_gateway.get_project_issues(project_id, params=params)
        elif resource == "pipelines":
            items = projects_gateway.get_project_pipelines(project_id, params=params)
        elif resource == "branches":
            items = projects_gateway.get_project_branches(project_id, params=params)
        else:
            items = []
        filtered_items = []
        for item in items:
            item_date = item.get(date_field)
            if not item_date:
                continue
            if last_date:
                if item_date > last_date:
                    filtered_items.append(item)
            else:
                filtered_items.append(item)
            if not max_date or item_date > max_date:
                max_date = item_date
        all_items[project_id] = filtered_items
    print(f"[DEBUG] {resource} last_date: {last_date}, max_date: {max_date}")
    if max_date and max_date != last_date:
        set_last_extraction_date(resource, max_date)
        print(f"[INFO] Date de dernière extraction {resource} mise à jour: {max_date}")
    else:
        print(f"[INFO] Aucune nouvelle date à enregistrer pour {resource}.")
    return all_items

def fetch_all_projects_events(projects_gateway, params=None):
    """
    Récupère tous les events pour chaque projet.
    :return: dict {project_id: [events]}
    """
    projects = projects_gateway.get_projects(params={"membership": True})
    print(f"[DEBUG] Nombre de projets extraits : {len(projects)}")
    all_events = {}
    for p in projects:
        project_id = p.get("id")
        project_name = p.get("name")
        events = projects_gateway.get_project_events(project_id, params=params)
        # Conversion en dict si besoin
        events_dicts = [e.attributes if hasattr(e, "attributes") else e for e in events]
        all_events[project_id] = events_dicts
        print(f"[DEBUG] {project_name} ({project_id}): {len(events_dicts)} events")
    return all_events

def fetch_all_projects_events_incremental(projects_gateway, params=None, date_field="created_at", api_param="after"):
    """
    Extraction incrémentielle des events pour chaque projet.
    """
    last_date = get_last_extraction_date("events")
    if last_date:
        if params is None:
            params = {}
        params = params.copy()
        params[api_param] = last_date
    projects = projects_gateway.get_projects(params={"membership": True})
    all_events = {}
    max_date = last_date
    for p in projects:
        project_id = p.get("id")
        project_name = p.get("name")
        events = projects_gateway.get_project_events(project_id, params=params)
        # Conversion en dict pour chaque event
        events_dicts = [e.attributes if hasattr(e, "attributes") else e for e in events]
        filtered_events = []
        for event in events_dicts:
            event_date = event.get(date_field)
            if not event_date:
                continue
            if last_date:
                if event_date > last_date:
                    filtered_events.append(event)
            else:
                filtered_events.append(event)
            if not max_date or event_date > max_date:
                max_date = event_date
        all_events[project_id] = filtered_events
    print(f"[DEBUG] events last_date: {last_date}, max_date: {max_date}")
    if max_date and max_date != last_date:
        set_last_extraction_date("events", max_date)
        print(f"[INFO] Date de dernière extraction events mise à jour: {max_date}")
    else:
        print(f"[INFO] Aucune nouvelle date à enregistrer pour events.")
    return all_events

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

    # Extraction complète des events (full)
    print("\n🗃️ Extraction des events par projet...")
    all_events = fetch_all_projects_events(projects_gateway, params={"membership": True})
    save_json(all_events, "projects_events_full.json")

    # Extraction incrémentielle des commits
    print("\n📄 Extraction incrémentielle des commits...")
    all_commits_incremental = fetch_all_projects_commits_incremental(projects_gateway)
    save_json(all_commits_incremental, "projects_commits_incremental.json")

    # Extraction incrémentielle des merge requests
    print("\n📄 Extraction incrémentielle des merge requests...")
    all_mrs_incremental = fetch_all_projects_resource_incremental(
        projects_gateway, "merge_requests", date_field="updated_at", api_param="updated_after"
    )
    save_json(all_mrs_incremental, "projects_merge_requests_incremental.json")

    # Extraction incrémentielle des issues
    print("\n📄 Extraction incrémentielle des issues...")
    all_issues_incremental = fetch_all_projects_resource_incremental(
        projects_gateway, "issues", date_field="updated_at", api_param="updated_after"
    )
    save_json(all_issues_incremental, "projects_issues_incremental.json")

    # Extraction incrémentielle des pipelines
    print("\n📄 Extraction incrémentielle des pipelines...")
    all_pipelines_incremental = fetch_all_projects_resource_incremental(
        projects_gateway, "pipelines", date_field="updated_at", api_param="updated_after"
    )
    save_json(all_pipelines_incremental, "projects_pipelines_incremental.json")

    # Extraction incrémentielle des branches (si applicable)
    print("\n📄 Extraction incrémentielle des branches...")
    all_branches_incremental = fetch_all_projects_branches_incremental(projects_gateway)
    save_json(all_branches_incremental, "projects_branches_incremental.json")

    # Extraction incrémentielle des events
    print("\n📄 Extraction incrémentielle des events...")
    all_events_incremental = fetch_all_projects_events_incremental(projects_gateway)
    save_json(all_events_incremental, "projects_events_incremental.json")

    print("\n✅ Extraction terminée.")

# Explication :
# - projects_commits_full.json : contient TOUS les commits de chaque projet (toute l'historique)
# - projects_commits_incremental.json : contient uniquement les commits NOUVEAUX depuis la dernière extraction
# - projects_issues_full.json / projects_issues_incremental.json : même logique pour les issues
# - projects_merge_requests_full.json / projects_merge_requests_incremental.json : même logique pour les merge requests
# - projects_pipelines_full.json / projects_pipelines_incremental.json : même logique pour les pipelines
# - projects_branches_full.json / projects_branches_incremental.json : même logique pour les branches
# - projects_events_full.json / projects_events_incremental.json : même logique pour les events
#
# Pour chaque ressource, *_full.json contient tout l'historique, *_incremental.json contient uniquement les nouveautés depuis la dernière extraction.
if __name__ == "__main__":
    main()
# Explication :
# - projects_commits_full.json : contient TOUS les commits de chaque projet (toute l'historique)
# - projects_commits_incremental.json : contient uniquement les commits NOUVEAUX depuis la dernière extraction
# - projects_issues_full.json / projects_issues_incremental.json : même logique pour les issues
# - projects_merge_requests_full.json / projects_merge_requests_incremental.json : même logique pour les merge requests
# - projects_pipelines_full.json / projects_pipelines_incremental.json : même logique pour les pipelines
# - projects_branches_full.json / projects_branches_incremental.json : même logique pour les branches
# - projects_events_full.json / projects_events_incremental.json : même logique pour les events
#
# Pour chaque ressource, *_full.json contient tout l'historique, *_incremental.json contient uniquement les nouveautés depuis la dernière extraction.
# Pour chaque ressource, *_full.json contient tout l'historique, *_incremental.json contient uniquement les nouveautés depuis la dernière extraction.
