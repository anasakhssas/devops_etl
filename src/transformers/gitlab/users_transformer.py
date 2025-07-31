from typing import List, Dict, Any

class UsersTransformer:
    """
    Transformateur pour les utilisateurs GitLab.
    """
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        transformed = []
        for user in data:
            transformed_user = {
                "id": user.get("id"),
                "username": user.get("username"),
                "name": user.get("name"),
                "email": user.get("email") if user.get("email") not in (None, '', 'null') else None,
                "is_admin": user.get("is_admin", False),
                "state": user.get("state"),
                "web_url": user.get("web_url"),
                "created_at": user.get("created_at") if user.get("created_at") not in (None, '', 'null') else None,
                "last_activity_on": user.get("last_activity_on") if user.get("last_activity_on") not in (None, '', 'null') else None,
                "group": user.get("group", None)
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
    exit(1)

    with open(input_json_path, "r", encoding="utf-8") as f:
        raw_users = json.load(f)

    transformer = UsersTransformer()
    transformed_users = transformer.transform(raw_users)

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(transformed_users, f, default=str, ensure_ascii=False, indent=2)

    print(f"[✅] Données transformées enregistrées dans : {output_json_path}")
