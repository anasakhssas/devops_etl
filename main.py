import os
import json
from dotenv import load_dotenv
from src.extractors.gitlab.gitlab_client_improved import GitLabClient
from src.extractors.gitlab.projects_gateway import GitLabProjectsGateway

def fetch_projects(projects_gateway, params=None):
    """
    Récupère les projets GitLab via la passerelle.
    :param projects_gateway: Instance de GitLabProjectsGateway
    :param params: Dictionnaire de paramètres optionnels pour le filtrage
    :return: Liste de projets (dictionnaires)
    """
    projects = projects_gateway.get_projects(params=params)

    print(f"[DEBUG] Nombre de projets extraits : {len(projects)}")
    return projects

def fetch_project_commits(projects_gateway, project_id, params=None):
    """
    Récupère les commits d'un projet GitLab via la passerelle.
    :param projects_gateway: Instance de GitLabProjectsGateway
    :param project_id: ID du projet GitLab
    :param params: Dictionnaire de paramètres optionnels pour le filtrage
    :return: Liste de commits (dictionnaires)
    """
    commits = projects_gateway.get_project_commits(project_id, params=params)
    print(f"[DEBUG] Nombre de commits extraits pour le projet {project_id} : {len(commits)}")
    return commits

def test_get_project_commits(projects_gateway, project_id):
    """
    Teste la récupération des commits d'un projet GitLab.
    :param projects_gateway: Instance de GitLabProjectsGateway
    :param project_id: ID du projet GitLab à tester
    """
    print(f"\n[TEST] Test de get_project_commits pour le projet ID: {project_id}")
    commits = projects_gateway.get_project_commits(project_id)
    print(f"[TEST] Nombre de commits récupérés: {len(commits)}")
    for i, commit in enumerate(commits[:3], start=1):
        print(f"   {i}. {commit.get('short_id', commit.get('id'))} - {commit.get('title', commit.get('message', '')).splitlines()[0]}")
    if len(commits) > 3:
        print(f"   ...et {len(commits)-3} autres commits.")

def fetch_all_projects_and_commits(projects_gateway, params=None):
    """
    Récupère tous les projets et les commits de chaque projet.
    :param projects_gateway: Instance de GitLabProjectsGateway
    :param params: Dictionnaire de paramètres optionnels pour le filtrage des projets
    :return: Dictionnaire {project_id: {"project": project_dict, "commits": [commit_dict, ...]}} 
    """
    projects = projects_gateway.get_projects(params=params)
    print(f"[DEBUG] Nombre de projets extraits : {len(projects)}")
    all_data = {}
    for i, project in enumerate(projects, start=1):
        project_id = project['id']
        print(f"\n[{i}] 📁 {project['name']} (ID: {project_id})")
        commits = projects_gateway.get_project_commits(project_id)
        print(f"   Nombre de commits: {len(commits)}")
        for j, commit in enumerate(commits[:3], start=1):
            print(f"      {j}. {commit.get('short_id', commit.get('id'))} - {commit.get('title', commit.get('message', '')).splitlines()[0]}")
        if len(commits) > 3:
            print(f"      ...et {len(commits)-3} autres commits.")
        all_data[project_id] = {"project": project, "commits": commits}
    return all_data

def fetch_projects_commits_count(projects_gateway, params=None):
    """
    Récupère tous les projets et le nombre de commits de chaque projet.
    :return: dict {nom_du_projet: nombre_de_commits}
    """
    projects = projects_gateway.get_projects(params=params)
    result = {}
    for project in projects:
        project_id = project['id']
        project_name = project['name']
        commits = projects_gateway.get_project_commits(project_id)
        result[project_name] = len(commits)
    return result

def test_projects_gateway_methods(projects_gateway, params=None):
    """
    Teste toutes les méthodes publiques de GitLabProjectsGateway sur les projets récupérés.
    Retourne un dictionnaire structuré avec les résultats.
    """
    result = {}
    projects = projects_gateway.get_projects(params=params)
    if not projects:
        print("Aucun projet trouvé pour les tests.")
        return {}

    first_project = projects[0]
    project_id = first_project['id']
    project_name = first_project['name']
    result['project_tested'] = {"id": project_id, "name": project_name}

    # Test get_projects
    result['get_projects'] = {"count": len(projects)}

    # Test get_project_members
    try:
        members = projects_gateway.get_project_members(project_id)
        result['get_project_members'] = {"count": len(members)}
    except Exception as e:
        result['get_project_members'] = {"error": str(e)}

    # Test get_project_commits
    try:
        commits = projects_gateway.get_project_commits(project_id)
        result['get_project_commits'] = {"count": len(commits)}
    except Exception as e:
        result['get_project_commits'] = {"error": str(e)}

    # Test get_project_merge_requests
    try:
        mrs = projects_gateway.get_project_merge_requests(project_id)
        result['get_project_merge_requests'] = {"count": len(mrs)}
    except Exception as e:
        result['get_project_merge_requests'] = {"error": str(e)}

    # Test get_project_issues
    try:
        issues = projects_gateway.get_project_issues(project_id)
        result['get_project_issues'] = {"count": len(issues)}
    except Exception as e:
        result['get_project_issues'] = {"error": str(e)}

    # Test get_project_pipelines
    try:
        pipelines = projects_gateway.get_project_pipelines(project_id)
        result['get_project_pipelines'] = {"count": len(pipelines)}
    except Exception as e:
        result['get_project_pipelines'] = {"error": str(e)}

    # Test get_project_branches
    try:
        branches = projects_gateway.get_project_branches(project_id)
        result['get_project_branches'] = {"count": len(branches)}
    except Exception as e:
        result['get_project_branches'] = {"error": str(e)}

    return result

def main():
    # Charger les variables d'environnement
    load_dotenv()

    private_token = os.getenv("GITLAB_PRIVATE_TOKEN")
    if not private_token:
        raise ValueError("⚠️ Le token privé GitLab (GITLAB_PRIVATE_TOKEN) est manquant dans le fichier .env.")

    gitlab_api_url = os.getenv("GITLAB_API_URL", "https://gitlab.com").rstrip("/")
    if not gitlab_api_url.endswith("/api/v4"):
        gitlab_api_url += "/api/v4"

    gitlab_config = {
        "api_url": gitlab_api_url,
        "private_token": private_token,
        "timeout": int(os.getenv("GITLAB_TIMEOUT", 10)),
        "max_retries": int(os.getenv("GITLAB_MAX_RETRIES", 3)),
        "retry_delay": int(os.getenv("GITLAB_RETRY_DELAY", 2)),
        "verify_ssl": os.getenv("GITLAB_VERIFY_SSL", "true").lower() == "true"
    }

    # Initialiser client GitLab
    client = GitLabClient(gitlab_config)
    projects_gateway = GitLabProjectsGateway(client)

    # Affiche la liste des projets récupérés
    projects = fetch_projects(projects_gateway, params={"membership": True})
    print(json.dumps(projects, indent=2, ensure_ascii=False))

    # Génère le dictionnaire {projet: nombre de commits}
    commits_count = fetch_projects_commits_count(projects_gateway, params={"membership": True})
    print(json.dumps(commits_count, indent=2, ensure_ascii=False))

    # Test de toutes les méthodes de projects_gateway.py avec sortie structurée
    test_results = test_projects_gateway_methods(projects_gateway, params={"membership": True})
    print(json.dumps(test_results, indent=2, ensure_ascii=False))

    # Remplace la logique précédente par l'appel à la nouvelle fonction :
    # fetch_all_projects_and_commits(projects_gateway, params={"membership": True})

    # if projects:
    #     print("✅ Projets récupérés avec succès :")
    #     for i, project in enumerate(projects, start=1):
    #         print(f"{i}. 📁 {project['name']} - ID: {project['id']}")
    #     # Tester la récupération des commits du premier projet
    #     first_project = projects[0]
    #     project_id = first_project['id']
    #     commits = fetch_project_commits(projects_gateway, project_id)
    #     if commits:
    #         print(f"\n✅ Commits du projet '{first_project['name']}' (ID: {project_id}) :")
    #         for j, commit in enumerate(commits[:5], start=1):
    #             print(f"   {j}. {commit.get('short_id', commit.get('id'))} - {commit.get('title', commit.get('message', '')).splitlines()[0]}")
    #         if len(commits) > 5:
    #             print(f"   ...et {len(commits)-5} autres commits.")
    #     else:
    #         print(f"❌ Aucun commit trouvé pour le projet '{first_project['name']}' (ID: {project_id}).")
    #     # Appel du test pour get_project_commits
    #     test_get_project_commits(projects_gateway, project_id)
    # else:
    #     print("❌ Aucun projet trouvé ou erreur lors de la récupération.")


if __name__ == "__main__":
    main()
