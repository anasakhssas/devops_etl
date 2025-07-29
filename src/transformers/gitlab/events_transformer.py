from typing import List, Dict, Any
from datetime import datetime
import os
import json

class EventsTransformer:
    """
    Transformateur pour les événements GitLab.
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
        for event in data:
            transformed_event = {
                "id": event.get("id"),
                "action_name": event.get("action_name"),
                "target_type": event.get("target_type"),
                "author_username": event.get("author", {}).get("username") or event.get("author_username"),
                "created_at": parse_date(event.get("created_at")),
                "target_title": event.get("target_title"),
                "target_id": event.get("target_id"),
                "project_id": event.get("project_id"),
                "author_id": event.get("author_id")
            }
            transformed.append(transformed_event)
        return transformed

if __name__ == "__main__":
    # Local test
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_json_path = os.path.abspath(os.path.join(base_dir, "../../../data/output/projects_events_full.json"))
    output_json_path = os.path.abspath(os.path.join(base_dir, "../../../data/transformers/events_transformed.json"))

    if not os.path.exists(input_json_path):
        print(f"[ERREUR] Fichier introuvable : {input_json_path}")
        exit(1)

    with open(input_json_path, "r", encoding="utf-8") as f:
        projects_events = json.load(f)

    # Fusionner tous les événements de tous les projets dans une seule liste
    all_events = []
    for events_list in projects_events.values():
        all_events.extend(events_list)

    transformer = EventsTransformer()
    transformed = transformer.transform(all_events)

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(transformed, f, default=str, ensure_ascii=False, indent=2)
