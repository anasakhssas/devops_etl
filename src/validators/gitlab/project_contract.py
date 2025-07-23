
from typing import Dict, Any

def validate_project(project: Dict[str, Any]) -> bool:
    """
    Valide qu'un dictionnaire projet GitLab respecte le contrat attendu.
    Lève une ValueError si un champ obligatoire est manquant ou invalide.
    """
    required_fields = ["id", "name", "created_at"]
    for field in required_fields:
        if field not in project or project[field] is None:
            raise ValueError(f"Champ obligatoire manquant ou nul: {field}")

    # Vérification de types simples (optionnel)
    if not isinstance(project["id"], int):
        raise ValueError("Le champ 'id' doit être un entier")
    if not isinstance(project["name"], str):
        raise ValueError("Le champ 'name' doit être une chaîne de caractères")

    # Ajoute d'autres règles métier si besoin

    return True

