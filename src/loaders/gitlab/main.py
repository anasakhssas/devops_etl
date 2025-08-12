import os
import sys
import subprocess

# Ajoute la racine du projet au PYTHONPATH pour que 'src' soit importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
# Optionnel : garder le PYTHONPATH du processus actuel mis à jour (l'environnement du sous-processus sera défini explicitement)
os.environ["PYTHONPATH"] = PROJECT_ROOT + os.pathsep + os.environ.get("PYTHONPATH", "")

def run_loader(loader_script):
    script_path = os.path.join(os.path.dirname(__file__), loader_script)
    print(f"\n[INFO] Exécution de {loader_script} ...")

    # Construire un environnement propre pour le sous-processus
    env = os.environ.copy()
    env["PYTHONPATH"] = PROJECT_ROOT + os.pathsep + env.get("PYTHONPATH", "")

    # Utiliser le même interpréteur et définir le répertoire de travail à la racine du projet
    result = subprocess.run([sys.executable, script_path], cwd=PROJECT_ROOT, env=env)
    exit_code = result.returncode

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
