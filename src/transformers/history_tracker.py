from typing import List, Dict, Any

class HistoryTracker:
    """
    Classe utilitaire pour suivre l'historique des transformations de données.
    """
    def __init__(self):
        """
        Initialise le tracker avec une liste vide d'historique.
        """
        self.history: List[Dict[str, Any]] = []

    def add_record(self, step: str, input_data: Any, output_data: Any, metadata: Dict[str, Any] = None):
        """
        Ajoute un enregistrement à l'historique.

        Args:
            step: Nom ou description de l'étape de transformation.
            input_data: Données d'entrée de l'étape.
            output_data: Données de sortie de l'étape.
            metadata: Métadonnées optionnelles (timestamp, utilisateur, etc).
        """
        record = {
            'step': step,
            'input': input_data,
            'output': output_data,
            'metadata': metadata or {}
        }
        self.history.append(record)

    def get_history(self) -> List[Dict[str, Any]]:
        """
        Retourne l'historique complet des transformations.
        """
        return self.history

    def clear(self):
        """
        Réinitialise l'historique.
        """
        self.history.clear()
    