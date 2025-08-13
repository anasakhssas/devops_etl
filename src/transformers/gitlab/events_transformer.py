from typing import List, Dict, Any
from datetime import datetime
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
        missing_target_type_count = 0
        
        for event in data:
            # Check if target_type is missing
            if event.get("target_type") is None:
                missing_target_type_count += 1
                # Log details about the event to help with debugging
                logger.warning(f"Event ID {event.get('id')} missing target_type. Action: {event.get('action_name')}")
                
                # Try to infer target_type from action_name or other fields
                inferred_type = self._infer_target_type(event)
                if inferred_type:
                    logger.info(f"Inferred target_type '{inferred_type}' for event ID {event.get('id')}")
            
            transformed_event = {
                "id": event.get("id"),
                "action_name": event.get("action_name"),
                "target_type": event.get("target_type") or self._infer_target_type(event) or "unknown",
                "author_username": event.get("author", {}).get("username") or event.get("author_username"),
                "created_at": parse_date_str_iso(event.get("created_at")),
                "target_title": event.get("target_title"),
                "target_id": event.get("target_id"),
                "project_id": event.get("project_id"),
                "author_id": event.get("author_id")
            }
            transformed.append(transformed_event)
            
        if missing_target_type_count > 0:
            logger.warning(f"Found {missing_target_type_count} events with missing target_type out of {len(data)} total events")
            
        return transformed
    
    def _infer_target_type(self, event: Dict[str, Any]) -> str:
        """
        Try to infer the target_type based on action_name or other fields.
        Returns inferred type or None if can't be determined.
        """
        action = event.get("action_name", "").lower()
        
        # Common mapping patterns based on GitLab event types
        if "issue" in action:
            return "Issue"
        elif "merge" in action:
            return "MergeRequest"
        elif "commit" in action:
            return "Commit"
        elif "pipeline" in action:
            return "Pipeline"
        elif "project" in action:
            return "Project"
        elif "note" in action or "comment" in action:
            return "Note"
        
        # If we can't infer, return None
        return None

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
