
from typing import Dict, Any

def validate_pipeline(pipeline: Dict[str, Any]) -> bool:
    """
    Valide qu'un dictionnaire pipeline GitLab respecte le contrat attendu.
    Lève une ValueError si un champ obligatoire est manquant ou invalide.
    """
    required_fields = ["id", "status", "ref", "created_at"]
    for field in required_fields:
        if field not in pipeline or pipeline[field] is None:
            raise ValueError(f"Champ obligatoire manquant ou nul: {field}")

    if not isinstance(pipeline["id"], int):
        raise ValueError("Le champ 'id' doit être un entier")
    if not isinstance(pipeline["status"], str):
        raise ValueError("Le champ 'status' doit être une chaîne de caractères")
    if not isinstance(pipeline["ref"], str):
        raise ValueError("Le champ 'ref' doit être une chaîne de caractères")

    # Ajoute d'autres règles métier si besoin

    return True
