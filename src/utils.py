import os
import json

STATE_FILE = "data/etl_state.json"
def save_json(data, filename, folder="data/output"):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[✅] Données sauvegardées dans : {path}")
def get_last_extraction_date(resource: str) -> str:
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
    return state.get(resource)

def set_last_extraction_date(resource: str, date_str: str):
    state = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
    state[resource] = date_str
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
