from typing import List, Dict, Any
from datetime import datetime
import os
import json

class EventsTransformer:
    """
    Transformateur pour les événements GitLab.
    """

    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        def parse_date_str_iso(date_str: Any) -> Any:
            # Retourne une chaîne ISO si possible, sinon la valeur d'origine (ou None).
            if not date_str:
                return None
            if isinstance(date_str, datetime):
                return date_str.isoformat()
            if isinstance(date_str, str):
                # Essais de parsing pour formats courants GitLab
                for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        return dt.isoformat()
                    except ValueError:
                        pass
                # Dernière tentative: fromisoformat (gère "YYYY-MM-DD HH:MM:SS" et "YYYY-MM-DDTHH:MM:SS[.ffffff][+/-offset]")
                try:
                    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    return dt.isoformat()
                except Exception:
                    return date_str
            return date_str

        transformed = []
        for event in data:
            transformed_event = {
                "id": event.get("id"),
                "action_name": event.get("action_name"),
                "target_type": event.get("target_type"),
                "author_username": event.get("author", {}).get("username") or event.get("author_username"),
                "created_at": parse_date_str_iso(event.get("created_at")),
                "target_title": event.get("target_title"),
                "target_id": event.get("target_id"),
                "project_id": event.get("project_id"),
                "author_id": event.get("author_id")
            }
            transformed.append(transformed_event)
        return transformed

def run(input_json_path: str = None, output_json_path: str = None) -> None:
    # Détermine les chemins par défaut relativement au repo
    base_dir = os.path.dirname(os.path.abspath(__file__))
    default_input = os.path.abspath(os.path.join(base_dir, "../../../data/output/projects_events_incremental.json"))
    default_output = os.path.abspath(os.path.join(base_dir, "../../../data/transformers/events_transformed.json"))
    input_path = input_json_path or default_input
    output_path = output_json_path or default_output

    if not os.path.exists(input_path):
        print(f"[ERREUR] Fichier introuvable : {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        projects_events = json.load(f)

    # Aplatit la structure quelle que soit la forme (dict par projet ou liste directe)
    all_events = []
    if isinstance(projects_events, dict):
        for v in projects_events.values():
            if isinstance(v, list):
                all_events.extend(v)
            elif isinstance(v, dict) and isinstance(v.get("events"), list):
                all_events.extend(v["events"])
    elif isinstance(projects_events, list):
        all_events = projects_events

    print(f"[ℹ️] Événements en entrée: {len(all_events)}")

    transformer = EventsTransformer()
    transformed = transformer.transform(all_events)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(transformed, f, ensure_ascii=False, indent=2)

    print(f"[✅] Fichier transformé écrit: {output_path} ({len(transformed)} événements)")

if __name__ == "__main__":
    run()
