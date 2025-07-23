"""
Ce module exporte les entités du domaine définies dans entities.py.
"""

import sys
import os
import importlib.util

# Chemin vers le fichier entities.py parent
parent_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "entities.py"))

# Charger le module
spec = importlib.util.spec_from_file_location("domain_entities", parent_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Exposer les classes
Project = module.Project
Developer = module.Developer
CodeQualityMetric = module.CodeQualityMetric
Commit = module.Commit
SecurityVulnerability = module.SecurityVulnerability

# Exposer les classes
__all__ = ['Project', 'Developer', 'CodeQualityMetric', 'Commit', 'SecurityVulnerability']
