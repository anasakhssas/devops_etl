import sys
from pathlib import Path

# Ajoute le répertoire src au PYTHONPATH
root_path = Path(__file__).resolve().parent
sys.path.insert(0, str(root_path))