import os
import json
import pandas as pd
from pandas import json_normalize

def clean_list_of_dicts(data):
    # Aplatir la liste de dicts, aplatir les colonnes imbriquées
    df = json_normalize(data)

    # Suppression colonnes vides
    df = df.dropna(how="all", axis=1)

    # Suppression doublons
    df = df.drop_duplicates()

    # Trim des espaces pour les colonnes strings
    df = df.apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x))

    return df.to_dict(orient="records")


# Dossiers
RAW_DATA_DIR = "data/output"
TRANSFORMED_DATA_DIR = "data/transformers"

# --- Fonction générique de sauvegarde ---
def save_json(data, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- Chargement d'un fichier brut ---
def load_json(file_name):
    file_path = os.path.join(RAW_DATA_DIR, file_name)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# --- Nettoyage générique ---
def clean_list_of_dicts(data):
    df = pd.json_normalize(data)

    # Transformer les colonnes contenant des listes en chaînes JSON
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, list)).any():
            df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, list) else x)

    df = df.dropna(how="all", axis=1)
    df = df.drop_duplicates()
    df = df.apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x))

    return df.to_dict(orient="records")

if __name__ == "__main__":
    print("[INFO] Début de la transformation SonarQube...")

    # Fichiers à traiter
    files_mapping = {
        "sonarqube_projects.json": "sonarqube_projects_clean.json",
        "sonarqube_full_extract.json": "sonarqube_measures_clean.json",
     #   "sonarqube_issues.json": "sonarqube_issues_clean.json",
        "sonarqube_projects_resources_full.json": "sonarqube_branches_clean.json",
    #    "sonarqube_quality_gate.json": "sonarqube_quality_gate_clean.json"
    }

    for raw_file, clean_file in files_mapping.items():
       file_path = os.path.join(RAW_DATA_DIR, raw_file)  # <-- définir ici file_path
       print(f"[INFO] Traitement de {raw_file}...")
    
       if not os.path.exists(file_path):
          print(f"[WARN] Fichier manquant, passage au suivant : {raw_file}")
          continue

    raw_data = load_json(raw_file)
    cleaned_data = clean_list_of_dicts(raw_data)
    save_json(cleaned_data, os.path.join(TRANSFORMED_DATA_DIR, clean_file))

    print("[INFO] Transformation terminée avec succès.")
