"""
Ce module exporte les objets de valeur du domaine définis dans value_objects.py.
"""

import importlib.util
import sys
import os

# Chemin vers le fichier value_objects.py parent
parent_file = os.path.join(os.path.dirname(__file__), "..", "value_objects.py")

# Charger le module
spec = importlib.util.spec_from_file_location("domain_values", parent_file)
domain_values = importlib.util.module_from_spec(spec)
sys.modules["domain_values"] = domain_values
spec.loader.exec_module(domain_values)

# Exposer les classes
DateRange = domain_values.DateRange
CommitActivity = domain_values.CommitActivity
ProjectIdentifier = domain_values.ProjectIdentifier
CodeCoverage = domain_values.CodeCoverage
TechnicalDebt = domain_values.TechnicalDebt
MetricValue = domain_values.MetricValue

__all__ = [
    'DateRange', 'CommitActivity', 'ProjectIdentifier',
    'CodeCoverage', 'TechnicalDebt', 'MetricValue'
]
