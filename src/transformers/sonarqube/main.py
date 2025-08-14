import os
import json
from datetime import datetime

# ========================
# Configuration des chemins
# ========================

# Dossier où se trouve ce script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Dossiers d'entrée et de sortie (relatifs à BASE_DIR)
INPUT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../data/output/sonarqube"))
OUTPUT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../data/transformes/sonarqube"))

# ========================
# Fonctions utilitaires
# ========================

def load_json_files(input_dir):
    """Charge tous les fichiers JSON d'un dossier."""
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"[ERREUR] Dossier introuvable : {input_dir}")
    
    data = []
    for fname in os.listdir(input_dir):
        if fname.endswith(".json"):
            with open(os.path.join(input_dir, fname), "r", encoding="utf-8") as f:
                try:
                    data.append(json.load(f))
                except json.JSONDecodeError:
                    print(f"[AVERTISSEMENT] Fichier JSON invalide ignoré : {fname}")
    return data

def write_json(data, filename):
    """Écrit des données dans un fichier JSON."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Fichier écrit : {filepath}")

def append_json_history(data, filename):
    """Ajoute les nouvelles données à un fichier d'historique JSON."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    history = []
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                print(f"[AVERTISSEMENT] Historique corrompu, réinitialisation.")
    history.extend(data)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Historique mis à jour : {filepath}")

# ========================
# Fonctions de transformation
# ========================

def transform_projects(data):
    """Transforme les données brutes en dimensions projets."""
    projects = []
    for item in data:
        # Si la clé 'projects' existe et est une liste
        if "projects" in item and isinstance(item["projects"], list):
            for project in item["projects"]:
                projects.append({
                    "id": project.get("id"),
                    "key": project.get("key"),
                    "name": project.get("name"),
                    "visibility": project.get("visibility", "private")
                })
        # Sinon, structure ancienne
        elif "project" in item:
            projects.append({
                "id": item["project"].get("id"),
                "key": item["project"].get("key"),
                "name": item["project"].get("name"),
                "visibility": item["project"].get("visibility", "private")
            })
    return projects

def extract_metric(measures, metric_name):
    for m in measures:
        if m.get("metric") == metric_name:
            return m.get("value", "0")
    return "0"

def transform_metrics(data):
    """Transforme les données brutes en métriques projets au format attendu."""
    metrics = []
    extraction_date = int(datetime.now().strftime("%Y%m%d"))

    def process_project(item):
        # Vérifie la présence des mesures SonarQube
        if (
            isinstance(item, dict)
            and "project" in item
            and "measures" in item
            and "component" in item["measures"]
            and "measures" in item["measures"]["component"]
        ):
            project_key = item["project"].get("key")
            branch_name = "main"
            if "branches" in item and isinstance(item["branches"], list) and item["branches"]:
                branch_name = item["branches"][0].get("name", "main")
            measures = item["measures"]["component"]["measures"]
            metrics.append({
                "project_key": project_key,
                "date_id": extraction_date,
                "branch_name": branch_name,
                "n_bugs": extract_metric(measures, "bugs"),
                "n_vulnerabilities": extract_metric(measures, "vulnerabilities"),
                "n_code_smells": extract_metric(measures, "code_smells"),
                "n_hotspots": extract_metric(measures, "security_hotspots"),
                "n_duplicated_lines": extract_metric(measures, "duplicated_lines_density"),
                "coverage": extract_metric(measures, "coverage"),
                "complexity": extract_metric(measures, "complexity"),
                "n_lines_of_code": extract_metric(measures, "lines_to_cover"),
                "extraction_date": extraction_date
            })

    # Parcours récursif pour trouver tous les projets
    def recursive_search(obj):
        if isinstance(obj, dict):
            process_project(obj)
            for v in obj.values():
                recursive_search(v)
        elif isinstance(obj, list):
            for elem in obj:
                recursive_search(elem)

    recursive_search(data)
    return metrics

def transform_issues(data):
    """Transforme les données brutes en issues."""
    issues = []
    for item in data:
        # Si la clé 'issues' existe et est une liste
        if "issues" in item and isinstance(item["issues"], list):
            for issue in item["issues"]:
                issues.append({
                    "project_id": issue.get("project_id") or item.get("project_id"),
                    "key": issue.get("key"),
                    "type": issue.get("type"),
                    "severity": issue.get("severity"),
                    "status": issue.get("status")
                })
    return issues

def transform_projects_simple(data):
    """Transforme les données brutes en liste simple de projets."""
    projects = []

    def process_project(item):
        if isinstance(item, dict) and "project" in item:
            project = item["project"]
            projects.append({
                "project_key": project.get("key"),
                "project_name": project.get("name"),
                "language": project.get("language"),  # <-- essaie d'extraire la langue si présente
                "visibility": project.get("visibility", "private"),
                "created_at": project.get("lastAnalysisDate")
            })

    def recursive_search(obj):
        if isinstance(obj, dict):
            process_project(obj)
            for v in obj.values():
                recursive_search(v)
        elif isinstance(obj, list):
            for elem in obj:
                recursive_search(elem)

    recursive_search(data)
    return projects

# ========================
# Point d'entrée principal
# ========================

def main():
    print(f"[INFO] Lecture des fichiers depuis : {INPUT_DIR}")
    print(f"[INFO] Les fichiers transformés seront enregistrés dans : {OUTPUT_DIR}")

    # Charger les données brutes
    raw_data = load_json_files(INPUT_DIR)
    print(f"[DEBUG] Données brutes chargées : {json.dumps(raw_data, indent=2, ensure_ascii=False)}")

    # Écrire la liste simple des projets
    projects_simple = transform_projects_simple(raw_data)
    write_json(projects_simple, "projects_simple.json")

    # Écrire les métriques du jour
    today_str = datetime.now().strftime("%Y%m%d")
    metrics_today = transform_metrics(raw_data)
    print(f"[DEBUG] Métriques transformées : {json.dumps(metrics_today, indent=2, ensure_ascii=False)}")
    write_json(metrics_today, f"fact_project_metrics_{today_str}.json")

    # Mettre à jour l'historique des métriques
    append_json_history(metrics_today, "fact_project_metrics_history.json")

if __name__ == "__main__":
    main()
