import json
import os
from datetime import datetime

STATE_FILE = "data/etl_state.json"

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
