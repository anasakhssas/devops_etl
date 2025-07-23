
from typing import Dict, Any

def validate_issue(issue: Dict[str, Any]) -> bool:
    """
    Valide qu'un dictionnaire issue GitLab respecte le contrat attendu.
    Lève une ValueError si un champ obligatoire est manquant ou invalide.
    """
    required_fields = ["id", "title", "state", "created_at"]
    for field in required_fields:
        if field not in issue or issue[field] is None:
            raise ValueError(f"Champ obligatoire manquant ou nul: {field}")

    if not isinstance(issue["id"], int):
        raise ValueError("Le champ 'id' doit être un entier")
    if not isinstance(issue["title"], str):
        raise ValueError("Le champ 'title' doit être une chaîne de caractères")
    if not isinstance(issue["state"], str):
        raise ValueError("Le champ 'state' doit être une chaîne de caractères")

    # Ajoute d'autres règles métier si besoin

    return True
