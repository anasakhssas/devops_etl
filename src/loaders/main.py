import os
import sys

def run_loader(loader_script):
    script_path = os.path.join(os.path.dirname(__file__), loader_script)
    print(f"\n[INFO] Exécution de {loader_script} ...")
    exit_code = os.system(f'python "{script_path}"')
    if exit_code != 0:
        print(f"[ERREUR] {loader_script} a échoué avec le code {exit_code}")
    else:
        print(f"[OK] {loader_script} terminé.")

if __name__ == "__main__":
    loaders = [
        "users_load.py",
        "load_projects.py",
        "load_branches.py",
        "load_commits.py",
        "load_issues.py",
        "load_merge_requests.py",
        "load_pipelines.py",
        "load_events.py"
    ]
    for loader in loaders:
        run_loader(loader)
    print("\n[✅] Tous les loaders ont été exécutés.")
