import os
import sys
import logging
from typing import Any, Dict, List, Optional

# Inclure le dossier racine du projet dans sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from dotenv import load_dotenv
from src.utils import save_json  # Utilitaire de sauvegarde JSON

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ajout: patcher dynamiquement src.core.exceptions pour fournir ConnectionError si absent
def _ensure_exceptions_patch() -> None:
    try:
        import importlib
        exc = importlib.import_module("src.core.exceptions")
        if not hasattr(exc, "ConnectionError"):
            import builtins
            setattr(exc, "ConnectionError", builtins.ConnectionError)
            logger.warning("Patched src.core.exceptions.ConnectionError -> builtins.ConnectionError")
    except Exception as e:
        logger.debug(f"Exceptions patch skipped: {e}")

# Exécuter le patch AVANT d'importer les modules SonarQube
_ensure_exceptions_patch()

# Importer ensuite les modules SonarQube
from src.extractors.sonarqube.factories import (
    SonarQubeClientFactory,
    SonarQubeGatewayFactory,
    SonarQubeExtractor,
)
from src.extractors.sonarqube.projects_gateway import SonarQubeProjectsGateway


def fetch_projects(projects_gateway: SonarQubeProjectsGateway,
                   organization: Optional[str] = None,
                   project_keys: Optional[List[str]] = None,
                   q: Optional[str] = None,
                   qualifiers: str = "TRK") -> List[Dict[str, Any]]:
    projects = projects_gateway.get_projects(
        organization=organization,
        project_keys=project_keys,
        q=q,
        qualifiers=qualifiers,
    )
    print(f"[INFO] Projets récupérés: {len(projects)}")
    return projects


def test_projects_gateway_methods(projects_gateway: SonarQubeProjectsGateway,
                                  project_key: str,
                                  branch: Optional[str] = None) -> Dict[str, Any]:
    """
    Teste quelques méthodes principales sur un projet donné.
    """
    result: Dict[str, Any] = {"project_key": project_key}

    # Détails projet
    try:
        result["project_details"] = projects_gateway.get_project(project_key)
    except Exception as e:
        result["project_details"] = {"error": str(e)}

    # Mesures qualité/couverture
    try:
        # Remplacer 'maintainability_rating' par 'sqale_rating'
        result["quality_measures"] = projects_gateway.get_project_quality_metrics(
            project_key, branch=branch,
            metrics=[
                "bugs", "reliability_rating", "vulnerabilities", "security_rating",
                "security_hotspots", "security_hotspots_reviewed", "code_smells",
                "sqale_index", "sqale_debt_ratio", "sqale_rating",  # <-- ici
                "duplicated_lines_density", "duplicated_blocks", "cognitive_complexity", "complexity"
            ]
        )
    except Exception as e:
        result["quality_measures"] = {"error": str(e)}
    try:
        result["coverage_measures"] = projects_gateway.get_project_code_coverage(project_key, branch=branch)
    except Exception as e:
        result["coverage_measures"] = {"error": str(e)}

    # Issues
    try:
        issues = projects_gateway.get_project_issues(project_key, branch=branch)
        result["issues_count"] = len(issues)
    except Exception as e:
        result["issues_count"] = {"error": str(e)}

    # Branches
    try:
        branches = projects_gateway.get_project_branches(project_key)
        result["branches_count"] = len(branches)
    except Exception as e:
        result["branches_count"] = {"error": str(e)}

    # Pull Requests (si disponible)
    try:
        prs = projects_gateway.get_project_pull_requests(project_key)
        result["pull_requests_count"] = len(prs)
    except Exception as e:
        result["pull_requests_count"] = {"error": str(e)}

    # Quality Gate
    try:
        qg = projects_gateway.get_quality_gate_status(project_key, branch=branch)
        result["quality_gate"] = qg
    except Exception as e:
        result["quality_gate"] = {"error": str(e)}

    # Compute Engine activity
    try:
        ce = projects_gateway.get_compute_engine_activity(project_key, branch=branch, only_current=False)
        result["ce_activity_count"] = len(ce)
    except Exception as e:
        result["ce_activity_count"] = {"error": str(e)}

    # Measures component tree (quelques métriques)
    try:
        components = projects_gateway.get_measures_component_tree(
            project_key=project_key,
            metrics=["ncloc", "complexity", "coverage"],
            branch=branch,
            qualifiers=["FIL", "DIR"],
            strategy="leaves",
        )
        result["component_tree_items"] = len(components) if isinstance(components, list) else 0
    except Exception as e:
        result["component_tree_items"] = {"error": str(e)}

    # Activity history (quelques métriques)
    try:
        history = projects_gateway.get_project_activity(
            project_key=project_key,
            metrics=["bugs", "vulnerabilities", "code_smells", "coverage"],
            branch=branch,
        )
        result["activity_history_metrics"] = list({m.get("metric") for m in history.get("measures", [])}) if isinstance(history, dict) else []
    except Exception as e:
        result["activity_history_metrics"] = {"error": str(e)}

    return result


def fetch_all_projects_resources(projects_gateway: SonarQubeProjectsGateway,
                                 project_keys: Optional[List[str]] = None,
                                 organization: Optional[str] = None,
                                 branch: Optional[str] = None) -> Dict[str, Any]:
    """
    Récupère pour chaque projet quelques ressources (mesures, issues, branches, quality gate, CE).
    """
    projects = projects_gateway.get_projects(organization=organization, project_keys=project_keys)
    print(f"[INFO] Projets extraits: {len(projects)}")

    all_data: Dict[str, Any] = {}
    for i, comp in enumerate(projects, start=1):
        proj_key = comp.get("key") or comp.get("project", {}).get("key")
        proj_name = comp.get("name") or proj_key
        if not proj_key:
            continue
        print(f"[{i}] {proj_name} (key: {proj_key})")

        entry: Dict[str, Any] = {"project": comp}
        try:
            # Remplacer 'maintainability_rating' par 'sqale_rating'
            entry["quality_measures"] = projects_gateway.get_project_quality_metrics(
                proj_key, branch=branch,
                metrics=[
                    "bugs", "reliability_rating", "vulnerabilities", "security_rating",
                    "security_hotspots", "security_hotspots_reviewed", "code_smells",
                    "sqale_index", "sqale_debt_ratio", "sqale_rating",  # <-- ici
                    "duplicated_lines_density", "duplicated_blocks", "cognitive_complexity", "complexity"
                ]
            )
        except Exception as e:
            entry["quality_measures"] = {"error": str(e)}

        try:
            entry["coverage_measures"] = projects_gateway.get_project_code_coverage(proj_key, branch=branch)
        except Exception as e:
            entry["coverage_measures"] = {"error": str(e)}

        try:
            entry["issues"] = projects_gateway.get_project_issues(proj_key, branch=branch)
        except Exception as e:
            entry["issues"] = {"error": str(e)}

        try:
            entry["branches"] = projects_gateway.get_project_branches(proj_key)
        except Exception as e:
            entry["branches"] = {"error": str(e)}

        try:
            entry["quality_gate"] = projects_gateway.get_quality_gate_status(proj_key, branch=branch)
        except Exception as e:
            entry["quality_gate"] = {"error": str(e)}

        try:
            entry["ce_activity"] = projects_gateway.get_compute_engine_activity(proj_key, branch=branch, only_current=False)
        except Exception as e:
            entry["ce_activity"] = {"error": str(e)}

        all_data[proj_key] = entry

    return all_data


def main():
    load_dotenv()

    # Config SonarQube
    api_url = os.getenv("SONARQUBE_API_URL", "https://sonarcloud.io/api").rstrip("/")
    token = os.getenv("SONARQUBE_TOKEN")
    username = os.getenv("SONARQUBE_USERNAME")
    password = os.getenv("SONARQUBE_PASSWORD")
    organization = os.getenv("SONARQUBE_ORGANIZATION")  # utile pour SonarCloud
    branch = os.getenv("SONARQUBE_BRANCH")
    project_keys_env = os.getenv("SONARQUBE_PROJECT_KEYS", "")
    project_keys = [k.strip() for k in project_keys_env.split(",") if k.strip()] or None

    config = {
        "api_url": api_url,
        "token": token,
        "username": username,
        "password": password,
        "timeout": int(os.getenv("SONARQUBE_TIMEOUT", "20")),
        "max_retries": int(os.getenv("SONARQUBE_MAX_RETRIES", "3")),
    }

    # Création client/gateway/extractor
    client = SonarQubeClientFactory.create_client(config=config)
    print("[INFO] Test de connexion SonarQube...")
    try:
        ok = client.test_connection()
        print(f"[INFO] Connexion: {'ok' if ok else 'failed'}")
    except Exception as e:
        print(f"[WARN] Échec test connexion: {e}")

    projects_gateway = SonarQubeGatewayFactory.create_projects_gateway(client)
    extractor = SonarQubeExtractor(config=config)

    # 1) Récupération des projets
    print("\n📂 Récupération des projets...")
    projects = fetch_projects(projects_gateway, organization=organization, project_keys=project_keys)
    save_json(projects, "sonarqube_projects.json")

    if not projects:
        print("[INFO] Aucun projet trouvé.")
        return

    # Choisir un projet de test
    first = projects[0]
    test_key = first.get("key") or first.get("project", {}).get("key")
    if not test_key:
        print("[WARN] Clé de projet introuvable dans le premier résultat.")
        return

    # 2) Tests des méthodes gateway sur un projet
    print("\n🧪 Tests des méthodes SonarQubeProjectsGateway...")
    tests = test_projects_gateway_methods(projects_gateway, project_key=test_key, branch=branch)
    save_json(tests, "sonarqube_tests_methods.json")

    # 3) Extraction "full" par projet via gateway (mesures, issues, branches, quality gate, CE)
    print("\n🗃️ Extraction des ressources par projet (gateway)...")
    all_resources = fetch_all_projects_resources(projects_gateway, project_keys=project_keys, organization=organization, branch=branch)
    save_json(all_resources, "sonarqube_projects_resources_full.json")

    # 4) Extraction "full" via Extractor (orchestration)
    print("\n📦 Extraction via SonarQubeExtractor...")
    full_extract = extractor.extract(
        organization=organization,
        project_keys=project_keys,
        include_issues=True,
        include_branches=True,
        include_quality_gate=True,
        include_activity=True,
        branch=branch,
        # metrics=["bugs", ..., "sqale_rating", ...]  # si extract() accepte ce paramètre
    )
    save_json(full_extract, "sonarqube_full_extract.json")

    # 5) Extraction incrémentielle (optionnelle si SONARQUBE_FROM_DATE défini)
    from_date = os.getenv("SONARQUBE_FROM_DATE")  # ex: "2024-01-01"
    to_date = os.getenv("SONARQUBE_TO_DATE")      # ex: "2024-12-31"
    if from_date:
        print("\n⏱️ Extraction incrémentielle...")
        inc_extract = extractor.extract_incremental(
            from_date=from_date,
            to_date=to_date,
            project_keys=project_keys,
            branch=branch,
            include_history_metrics=True,
            include_new_issues=True,
        )
        save_json(inc_extract, "sonarqube_incremental_extract.json")
    else:
        print("\n[INFO] SONARQUBE_FROM_DATE non défini, extraction incrémentielle ignorée.")

    print("\n✅ Extraction SonarQube terminée.")


if __name__ == "__main__":
    main()
