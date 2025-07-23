
from typing import List, Dict, Any
from datetime import datetime

class SCDHandler:
    """
    Gestionnaire pour appliquer le SCD Type 2 (Slowly Changing Dimension).
    """
    def apply_scd_type2(self,
                        current_data: List[Dict[str, Any]],
                        new_data: List[Dict[str, Any]],
                        key_fields: List[str],
                        effective_date_field: str = 'effective_date',
                        end_date_field: str = 'end_date',
                        current_flag_field: str = 'is_current',
                        now: datetime = None) -> List[Dict[str, Any]]:
        """
        Applique le SCD Type 2 :
        - Ferme les anciennes versions (en mettant à jour end_date et is_current)
        - Ajoute les nouvelles versions avec effective_date et is_current

        Args:
            current_data: Données existantes (historique).
            new_data: Nouvelles données à intégrer.
            key_fields: Liste des champs clés d'identification.
            effective_date_field: Nom du champ de début de validité.
            end_date_field: Nom du champ de fin de validité.
            current_flag_field: Nom du champ booléen indiquant la version courante.
            now: Datetime d'exécution (par défaut datetime.utcnow()).

        Returns:
            Liste de dictionnaires avec l'historique SCD2 mis à jour.
        """
        if now is None:
            now = datetime.utcnow()

        # Indexation des données existantes par clé
        current_index = {tuple(row[k] for k in key_fields): row for row in current_data if row.get(current_flag_field, True)}
        result = current_data.copy()

        for new_row in new_data:
            key = tuple(new_row[k] for k in key_fields)
            existing = current_index.get(key)
            if not existing:
                # Nouvelle entrée
                row = new_row.copy()
                row[effective_date_field] = now
                row[end_date_field] = None
                row[current_flag_field] = True
                result.append(row)
            else:
                # Vérifier si une modification a eu lieu (hors champs SCD)
                changed = any(new_row.get(f) != existing.get(f) for f in new_row if f not in [effective_date_field, end_date_field, current_flag_field])
                if changed:
                    # Fermer l'ancienne version
                    existing[end_date_field] = now
                    existing[current_flag_field] = False
                    # Ajouter la nouvelle version
                    row = new_row.copy()
                    row[effective_date_field] = now
                    row[end_date_field] = None
                    row[current_flag_field] = True
                    result.append(row)
        return result

