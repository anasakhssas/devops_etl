import os
import sys
import subprocess

# Racine du projet
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
os.environ["PYTHONPATH"] = PROJECT_ROOT + os.pathsep + os.environ.get("PYTHONPATH", "")

def run_loader(loader_script):
    """Exécute un script loader Python en sous-processus."""
    script_path = os.path.join(os.path.dirname(__file__), loader_script)
    print(f"\n[INFO] Exécution de {loader_script} ...")

    env = os.environ.copy()
    env["PYTHONPATH"] = PROJECT_ROOT + os.pathsep + env.get("PYTHONPATH", "")

    result = subprocess.run([sys.executable, script_path], cwd=PROJECT_ROOT, env=env)
    exit_code = result.returncode

    if exit_code != 0:
        print(f"[❌ ERREUR] {loader_script} a échoué avec le code {exit_code}")
    else:
        print(f"[✅ OK] {loader_script} terminé.")

def main():
    """Point d'entrée principal pour exécuter tous les loaders."""
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
    print("\n[🎯] Tous les loaders ont été exécutés.")

if __name__ == "__main__":
    main()
