
from typing import Dict, Any

def validate_branch(branch: Dict[str, Any]) -> bool:
    """
    Valide qu'un dictionnaire branch GitLab respecte le contrat attendu.
    Lève une ValueError si un champ obligatoire est manquant ou invalide.
    """
    required_fields = ["name", "commit"]
    for field in required_fields:
        if field not in branch or branch[field] is None:
            raise ValueError(f"Champ obligatoire manquant ou nul: {field}")

    if not isinstance(branch["name"], str):
        raise ValueError("Le champ 'name' doit être une chaîne de caractères")
    if not isinstance(branch["commit"], dict):
        raise ValueError("Le champ 'commit' doit être un dictionnaire")

    # Ajoute d'autres règles métier si besoin

    return True
