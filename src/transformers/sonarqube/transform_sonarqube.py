import os
import json
from datetime import datetime

INPUT_DIR = "data/output/sonarqube"
OUTPUT_DIR = "data/transformes/sonarqube"

def load_json_files(input_dir):
    data = []
    for fname in os.listdir(input_dir):
        if fname.endswith(".json"):
            with open(os.path.join(input_dir, fname), "r", encoding="utf-8") as f:
                data.append(json.load(f))
    return data

def flatten_projects(raw_data):
    # Suppose chaque fichier contient {"projects": [...]}
    projects = []
    for item in raw_data:
        if isinstance(item, dict) and "projects" in item:
            projects.extend(item["projects"])
        elif isinstance(item, list):
            projects.extend(item)
        else:
            projects.append(item)
    return projects

def transform_projects(raw_data):
    projects = []
    for item in flatten_projects(raw_data):
        projects.append({
            "project_key": item.get("key"),
            "project_name": item.get("name"),
            "language": item.get("language"),
            "visibility": item.get("visibility"),
            "created_at": item.get("creationDate")
        })
    return projects

def flatten_metrics(raw_data):
    metrics = []
    for item in raw_data:
        # Ajoutez ce print pour debug
        print("METRICS STRUCTURE:", item)
        # Adaptez ici selon la structure réelle
        if isinstance(item, dict) and "metrics" in item:
            metrics.extend(item["metrics"])
        elif isinstance(item, dict) and "projects" in item:
            for proj in item["projects"]:
                if "metrics" in proj:
                    metrics.extend(proj["metrics"])
                else:
                    metrics.append(proj)
        elif isinstance(item, list):
            metrics.extend(item)
        else:
            metrics.append(item)
    return metrics

def extract_metric(measures, metric_name):
    for m in measures:
        if m.get("metric") == metric_name:
            return m.get("value")
    return None

def transform_metrics(raw_data):
    metrics = []
    for item in flatten_metrics(raw_data):
        # Vérifie la structure attendue
        if isinstance(item, dict) and "project" in item and "measures" in item:
            project = item["project"]
            measures_list = item["measures"]["component"]["measures"]
            branches = item.get("branches", [])
            branch_name = branches[0]["name"] if branches else "main"
            analysis_date = branches[0].get("analysisDate") if branches else project.get("lastAnalysisDate")
            try:
                date_id = int(datetime.strptime(analysis_date, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y%m%d")) if analysis_date else None
            except Exception:
                date_id = None
            metrics.append({
                "project_key": project.get("key"),
                "date_id": date_id,
                "branch_name": branch_name,
                "n_bugs": extract_metric(measures_list, "bugs"),
                "n_vulnerabilities": extract_metric(measures_list, "vulnerabilities"),
                "n_code_smells": extract_metric(measures_list, "code_smells"),
                "n_hotspots": extract_metric(measures_list, "security_hotspots"),
                "n_duplicated_lines": extract_metric(measures_list, "duplicated_lines_density"),
                "coverage": extract_metric(measures_list, "coverage"),
                "complexity": extract_metric(measures_list, "complexity"),
                "n_lines_of_code": extract_metric(measures_list, "lines_to_cover")
            })
        # ...sinon, ignore ou ajoute une gestion spécifique si besoin...
    return metrics

def flatten_issues(raw_data):
    # Suppose chaque fichier contient {"issues": [...]}
    issues = []
    for item in raw_data:
        if isinstance(item, dict) and "issues" in item:
            issues.extend(item["issues"])
    return issues

def transform_issues(raw_data):
    issues = []
    for issue in flatten_issues(raw_data):
        try:
            date_id = int(datetime.strptime(issue.get("creationDate"), "%Y-%m-%dT%H:%M:%S%z").strftime("%Y%m%d"))
        except Exception:
            date_id = None
        issues.append({
            "issue_id": issue.get("key"),
            "project_key": issue.get("project"),
            "rule_key": issue.get("rule"),
            "date_id": date_id,
            "severity": issue.get("severity"),
            "status": issue.get("status"),
            "debt": issue.get("debt"),
            "message": issue.get("message")
        })
    return issues

def write_json(data, filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    raw_data = load_json_files(INPUT_DIR)
    write_json(transform_projects(raw_data), "dim_project.json")
    write_json(transform_metrics(raw_data), "fact_project_metrics.json")
    write_json(transform_issues(raw_data), "fact_issues.json")
    # Ajoutez d'autres transformations ici selon vos besoins

if __name__ == "__main__":
    main()
