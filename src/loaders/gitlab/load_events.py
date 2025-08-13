import os
import json
import sys
import logging
from datetime import datetime
# Assure l'import 'src.*' en ajoutant la racine du projet
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from src.loaders.database.db_connection import get_db_connection  # adapte le chemin si besoin

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _parse_datetime(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        # Accepte "Z", "T" ou espace
        candidate = value.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(candidate)
        except Exception:
            # Essais format GitLab classiques
            for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    pass
    return None

def load_events(json_path="data/transformers/events_transformed.json", check_overflow=False):
    """
    Charge et insère les événements depuis un fichier JSON vers la base de données.
    Si check_overflow=False, tente d'insérer même les grands IDs (risque d'erreur).
    """
    if not os.path.isabs(json_path):
        json_path = os.path.join(PROJECT_ROOT, json_path)

    print(f"[ℹ️] Lecture du fichier: {json_path}")
    if not os.path.exists(json_path):
        print(f"[❌] Fichier introuvable : {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        events = json.load(f)

    print(f"[ℹ️] Événements lus: {len(events) if isinstance(events, list) else 'inconnu'}")
    if not events:
        print("[ℹ️] Aucun événement à insérer.")
        return

    # Compte les événements sans target_type
    missing_target_type_count = 0
    for event in events:
        if isinstance(event, dict) and event.get("target_type") is None:
            missing_target_type_count += 1
    
    if missing_target_type_count > 0:
        logger.warning(f"Found {missing_target_type_count} events with missing target_type out of {len(events)} total events")

    try:
        conn = None
        cursor = None
        conn = get_db_connection()

        # Évite qu'une erreur sur une ligne n'aborte toutes les suivantes
        try:
            conn.autocommit = True
            print("[ℹ️] Autocommit activé pour des insertions résilientes.")
        except Exception:
            print("[ℹ️] Autocommit non disponible, utilisation du commit final.")

        cursor = conn.cursor()

        insert_query = """
        INSERT INTO events (
            id, action_name, target_type, author_username, 
            created_at, target_title, target_id, 
            project_id, author_id
        )
        VALUES (
            %(id)s, %(action_name)s, %(target_type)s, %(author_username)s,
            %(created_at)s, %(target_title)s, %(target_id)s,
            %(project_id)s, %(author_id)s
        )
        ON CONFLICT (id) DO NOTHING;
        """

        MAX_INT32 = 2_147_483_647
        success_count = 0
        skipped_overflow = 0

        for event in events:
            if not isinstance(event, dict):
                print(f"[⚠️] Événement ignoré (type invalide): {type(event)}")
                continue

            if not all(k in event for k in ("id", "created_at", "action_name")):
                print(f"[⚠️] Événement ignoré : clé(s) manquante(s) dans {event}")
                continue

            try:
                # Vérifie les dépassements INT4 sur les colonnes d'identifiants
                overflow_fields = []
                if check_overflow:  # Ajouter ce test pour pouvoir désactiver la vérification
                    for k in ("id", "target_id", "project_id", "author_id"):
                        v = event.get(k)
                        if v is None:
                            continue
                        try:
                            iv = int(v)
                            if iv > MAX_INT32:
                                overflow_fields.append(f"{k}={iv}")
                        except Exception:
                            # Si non convertible en int, on laisse la base rejeter si elle ne peut pas caster
                            pass

                if overflow_fields:
                    print(f"[⚠️] Ligne ignorée: valeurs > INT (probable besoin BIGINT) -> {', '.join(overflow_fields)}")
                    skipped_overflow += 1
                    continue

                event_data = {
                    "id": event.get("id"),
                    "action_name": event.get("action_name"),
                    "target_type": event.get("target_type"),
                    "author_username": event.get("author_username"),
                    "created_at": _parse_datetime(event.get("created_at")),
                    "target_title": event.get("target_title"),
                    "target_id": event.get("target_id"),
                    "project_id": event.get("project_id"),
                    "author_id": event.get("author_id"),
                }

                # Log when inserting an event with null target_type
                if event_data["target_type"] is None:
                    logger.warning(f"Inserting event ID={event_data['id']} with NULL target_type")
                
                cursor.execute(insert_query, event_data)
                success_count += 1

            except Exception as e:
                print(f"[⚠️] Erreur lors de l'insertion de l'événement ID={event.get('id')} : {str(e)}")

        # Commit seulement si autocommit non activé
        if not getattr(conn, "autocommit", False):
            conn.commit()

        total = len(events) if isinstance(events, list) else 0
        print(f"[✅] {success_count}/{total} événements insérés avec succès. Ignorés (overflow): {skipped_overflow}")

    except Exception as e:
        print(f"[❌] Erreur lors de la connexion ou l'insertion : {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    # Pour désactiver temporairement la vérification des dépassements:
    load_events(check_overflow=False)

