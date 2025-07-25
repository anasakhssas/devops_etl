from typing import List, Dict, Any
from datetime import datetime

class IssuesTransformer:
    """
    Transformateur pour les issues GitLab.
    """
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        def parse_date(date_str):
            if not date_str:
                return None
            try:
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                try:
                    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    return None

        transformed = []
        for issue in data:
            created_at = parse_date(issue.get("created_at"))
            updated_at = parse_date(issue.get("updated_at"))
            due_date = parse_date(issue.get("due_date")) if issue.get("due_date") else None
            transformed_issue = {
                "id": issue.get("id"),
                "title": issue.get("title"),
                "state": issue.get("state"),
                "created_at": created_at,
                "updated_at": updated_at,
                "author": issue.get("author", {}).get("name"),
                "web_url": issue.get("web_url"),
                "labels": issue.get("labels", []),
                "assignees": [assignee.get("name") for assignee in issue.get("assignees", [])],
                "due_date": due_date,
                "confidential": issue.get("confidential", False)
            }
            transformed.append(transformed_issue)
        return transformed

if __name__ == "__main__":
    import json
    import os

    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_json_path = os.path.abspath(os.path.join(base_dir, "../../../data/output/projects_issues_incremental.json"))
    output_json_path = os.path.abspath(os.path.join(base_dir, "../../../data/transformers/issues_transformed.json"))

    if not os.path.exists(input_json_path):
        print(f"[ERREUR] Fichier introuvable : {input_json_path}")
        exit(1)

    with open(input_json_path, "r", encoding="utf-8") as f:
        projects_issues = json.load(f)

    # Fusionner toutes les issues de tous les projets dans une seule liste
    all_issues = []
    for issues_list in projects_issues.values():
        all_issues.extend(issues_list)

    transformer = IssuesTransformer()
    transformed = transformer.transform(all_issues)

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(transformed, f, default=str, ensure_ascii=False, indent=2)
