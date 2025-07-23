
from typing import Dict, Any

def validate_user(user: Dict[str, Any]) -> bool:
    """
    Valide qu'un dictionnaire utilisateur GitLab respecte le contrat attendu.
    Lève une ValueError si un champ obligatoire est manquant ou invalide.
    """
    required_fields = ["id", "username", "name", "created_at"]
    for field in required_fields:
        if field not in user or user[field] is None:
            raise ValueError(f"Champ obligatoire manquant ou nul: {field}")

    if not isinstance(user["id"], int):
        raise ValueError("Le champ 'id' doit être un entier")
    if not isinstance(user["username"], str):
        raise ValueError("Le champ 'username' doit être une chaîne de caractères")
    if not isinstance(user["name"], str):
        raise ValueError("Le champ 'name' doit être une chaîne de caractères")

    # Ajoute d'autres règles métier si besoin

    return True
