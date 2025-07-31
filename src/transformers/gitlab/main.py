import os

def run_script(script_name):
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    print(f"\n[INFO] Exécution de {script_name} ...")
    exit_code = os.system(f'python "{script_path}"')
    if exit_code != 0:
        print(f"[ERREUR] {script_name} a échoué avec le code {exit_code}")
    else:
        print(f"[OK] {script_name} terminé.")

if __name__ == "__main__":
    scripts = [
        "users_transformer.py",
        "groups_transformer.py",
        "projects_transformer.py",
        "branches_transformer.py",
        "commits_transformer.py",
        "issues_transformer.py",
        "merge_requests_transformer.py",
        "pipelines_transformer.py",
        "events_transformer.py"
    ]
    for script in scripts:
        run_script(script)
    print("\n[✅] Tous les transformers ont été exécutés.")
