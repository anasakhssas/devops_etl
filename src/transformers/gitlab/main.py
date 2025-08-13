import os
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_script(script_name):
    """Exécute un script Python dans le même dossier."""
    script_path = os.path.join(BASE_DIR, script_name)
    print("\n" + "=" * 50)
    print(f"[INFO] Exécution de {script_name} ...")
    print("=" * 50)

    try:
        subprocess.run([sys.executable, script_path], check=True)
        print(f"[✅ OK] {script_name} terminé.")
    except subprocess.CalledProcessError as e:
        print(f"[❌ ERREUR] {script_name} a échoué. Code: {e.returncode}")
    except FileNotFoundError:
        print(f"[⚠️] Fichier introuvable : {script_name}")

def main():
    """Lance tous les scripts de transformation."""
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

    print("\n[🎯] Tous les transformers ont été exécutés.")

if __name__ == "__main__":
    main()
