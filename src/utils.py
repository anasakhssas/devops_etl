import os
import json

def save_json(data, filename, folder="data/output"):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[✅] Données sauvegardées dans : {path}")
