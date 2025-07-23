
from typing import Dict, Any

def validate_commit(commit: Dict[str, Any]) -> bool:
    """
    Valide qu'un dictionnaire commit GitLab respecte le contrat attendu.
    Lève une ValueError si un champ obligatoire est manquant ou invalide.
    """
    required_fields = ["id", "author_name", "created_at", "message"]
    for field in required_fields:
        if field not in commit or commit[field] is None:
            raise ValueError(f"Champ obligatoire manquant ou nul: {field}")

    if not isinstance(commit["id"], str):
        raise ValueError("Le champ 'id' doit être une chaîne de caractères (hash)")
    if not isinstance(commit["author_name"], str):
        raise ValueError("Le champ 'author_name' doit être une chaîne de caractères")
    if not isinstance(commit["message"], str):
        raise ValueError("Le champ 'message' doit être une chaîne de caractères")

    # Ajoute d'autres règles métier si besoin

    return True
