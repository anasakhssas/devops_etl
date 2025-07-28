from typing import List, Dict, Any
from datetime import datetime

class UsersTransformer:
    """
    Transformateur pour les utilisateurs GitLab.
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
        for user in data:
            transformed_user = {
                "id": user.get("id"),
                "username": user.get("username"),
                "name": user.get("name"),
                "email": user.get("email"),
                "is_admin": user.get("is_admin", False),
                "state": user.get("state"),
                "web_url": user.get("web_url"),
                "created_at": parse_date(user.get("created_at")),
                "last_activity_on": parse_date(user.get("last_activity_on")),
                "group": user.get("group", None)  # si tu as ajouté manuellement ce champ
            }
            transformed.append(transformed_user)
        return transformed


if __name__ == "__main__":
    import json
    import os

    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_json_path = os.path.abspath(os.path.join(base_dir, "../../../data/output/all_users.json"))
    output_json_path = os.path.abspath(os.path.join(base_dir, "../../../data/transformers/users_transformed.json"))

    if not os.path.exists(input_json_path):
        print(f"[ERREUR] Fichier introuvable : {input_json_path}")
        exit(1)

    with open(input_json_path, "r", encoding="utf-8") as f:
        raw_users = json.load(f)

    transformer = UsersTransformer()
    transformed_users = transformer.transform(raw_users)

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(transformed_users, f, default=str, ensure_ascii=False, indent=2)

    print(f"[✅] Données transformées enregistrées dans : {output_json_path}")
