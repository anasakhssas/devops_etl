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
        if "project" in item:
            projects.append({
                "id": item["project"].get("id"),
                "key": item["project"].get("key"),
                "name": item["project"].get("name"),
                "visibility": item["project"].get("visibility", "private")
            })
    return projects

def transform_metrics(data):
    """Transforme les données brutes en métriques projets."""
    metrics = []
    for item in data:
        if "metrics" in item:
            metrics.append({
                "project_id": item.get("project_id"),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "metrics": item["metrics"]
            })
    return metrics

def transform_issues(data):
    """Transforme les données brutes en issues."""
    issues = []
    for item in data:
        if "issues" in item:
            for issue in item["issues"]:
                issues.append({
                    "project_id": item.get("project_id"),
                    "key": issue.get("key"),
                    "type": issue.get("type"),
                    "severity": issue.get("severity"),
                    "status": issue.get("status")
                })
    return issues

# ========================
# Point d'entrée principal
# ========================

def main():
    print(f"[INFO] Lecture des fichiers depuis : {INPUT_DIR}")
    print(f"[INFO] Les fichiers transformés seront enregistrés dans : {OUTPUT_DIR}")

    # Charger les données brutes
    raw_data = load_json_files(INPUT_DIR)

    # Écrire la dimension projets
    write_json(transform_projects(raw_data), "dim_project.json")

    # Écrire les métriques du jour
    today_str = datetime.now().strftime("%Y%m%d")
    metrics_today = transform_metrics(raw_data)
    write_json(metrics_today, f"fact_project_metrics_{today_str}.json")

    # Mettre à jour l'historique des métriques
    append_json_history(metrics_today, "fact_project_metrics_history.json")

    # Écrire les issues
    write_json(transform_issues(raw_data), "fact_issues.json")

if __name__ == "__main__":
    main()
