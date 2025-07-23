"""
Implémentation GitLab du repository de développeurs.

Ce module contient l'adaptateur GitLab qui implémente l'interface DeveloperRepository
du domaine pour accéder aux données des développeurs depuis GitLab.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, cast

# Correction de l'importation pour utiliser le bon chemin
from src.domain.entities import Developer
from src.domain.repositories import DeveloperRepository
from src.adapters.gitlab.gitlab_client import GitLabClient


class GitLabDeveloperRepository(DeveloperRepository):
    """
    Implémentation du repository de développeurs utilisant l'API GitLab.
    """
    
    def __init__(self, gitlab_client: GitLabClient):
        """
        Initialise le repository avec un client GitLab.
        
        Args:
            gitlab_client: Client GitLab configuré
        """
        self.client = gitlab_client
    
    def get_all(self) -> List[Developer]:
        """
        Récupère tous les développeurs accessibles via l'API GitLab.
        
        Returns:
            Liste des développeurs
        """
        try:
            # Récupération des utilisateurs depuis l'API
            gitlab_users = self.client.get_users()
            
            # Conversion en entités du domaine
            return [self._to_domain_entity(user_data) for user_data in gitlab_users]
        except Exception as e:
            logging.error(f"Erreur lors de la récupération de tous les développeurs: {str(e)}")
            raise
    
    def get_by_id(self, developer_id: str) -> Optional[Developer]:
        """
        Récupère un développeur par son ID.
        
        Args:
            developer_id: ID du développeur
            
        Returns:
            Le développeur correspondant ou None s'il n'existe pas
        """
        try:
            user_data = self.client.get_user(developer_id)
            return self._to_domain_entity(user_data)
        except Exception as e:
            logging.error(f"Erreur lors de la récupération du développeur {developer_id}: {str(e)}")
            # Si l'utilisateur n'est pas trouvé, retourner None
            return None
    
    def get_by_username(self, username: str) -> Optional[Developer]:
        """
        Récupère un développeur par son nom d'utilisateur.
        
        Args:
            username: Nom d'utilisateur du développeur
            
        Returns:
            Le développeur correspondant ou None s'il n'existe pas
        """
        try:
            # L'API GitLab ne permet pas de rechercher directement par username,
            # donc on filtre les résultats de la recherche
            users = self.client.get_users(username=username)
            
            # Recherche exacte
            for user in users:
                if user.get('username') == username:
                    return self._to_domain_entity(user)
            
            # Utilisateur non trouvé
            return None
        except Exception as e:
            logging.error(f"Erreur lors de la récupération du développeur avec le username {username}: {str(e)}")
            raise
    
    def get_by_email(self, email: str) -> Optional[Developer]:
        """
        Récupère un développeur par son email.
        
        Args:
            email: Email du développeur
            
        Returns:
            Le développeur correspondant ou None s'il n'existe pas
        """
        try:
            # L'API GitLab ne permet pas de rechercher directement par email,
            # donc on filtre les résultats de la recherche
            users = self.client.get_users()
            
            # Recherche exacte
            for user in users:
                if user.get('email') == email:
                    return self._to_domain_entity(user)
            
            # Utilisateur non trouvé
            return None
        except Exception as e:
            logging.error(f"Erreur lors de la récupération du développeur avec l'email {email}: {str(e)}")
            raise
    
    def save(self, developer: Developer) -> Developer:
        """
        Sauvegarde un développeur (non implémenté car l'API GitLab ne permet généralement
        pas la création ou modification d'utilisateurs via des tokens standard).
        
        Args:
            developer: Le développeur à sauvegarder
            
        Returns:
            Le développeur sauvegardé
            
        Raises:
            NotImplementedError: Cette méthode n'est pas implémentée
        """
        # Note: La création/modification d'utilisateurs nécessite des permissions admin
        # et n'est généralement pas utilisée dans un contexte ETL
        raise NotImplementedError("La sauvegarde de développeurs n'est pas implémentée via l'API GitLab")
    
    def get_project_members(self, project_id: str) -> List[Developer]:
        """
        Récupère les membres d'un projet spécifique.
        
        Args:
            project_id: ID du projet
            
        Returns:
            Liste des développeurs membres du projet
        """
        try:
            # Récupération des membres du projet
            members_data = self.client.get_project_members(project_id)
            
            # Pour chaque membre, récupérer les informations détaillées de l'utilisateur
            developers = []
            for member in members_data:
                user_id = member.get('id')
                if user_id:
                    try:
                        user_data = self.client.get_user(user_id)
                        # Enrichir les données du membre avec les informations du rôle
                        user_data['role'] = member.get('access_level')
                        user_data['role_name'] = self._get_role_name(member.get('access_level'))
                        developers.append(self._to_domain_entity(user_data))
                    except Exception as inner_e:
                        logging.warning(f"Impossible de récupérer les détails de l'utilisateur {user_id}: {str(inner_e)}")
                        # Créer quand même un développeur avec les informations disponibles
                        user_data = {
                            'id': user_id,
                            'name': member.get('name', ''),
                            'username': member.get('username', ''),
                            'role': member.get('access_level'),
                            'role_name': self._get_role_name(member.get('access_level'))
                        }
                        developers.append(self._to_domain_entity(user_data))
            
            return developers
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des membres du projet {project_id}: {str(e)}")
            raise
    
    def get_by_project(self, project_id: str) -> List[Developer]:
        """
        Alias pour get_project_members pour la compatibilité avec l'interface du domaine.
        
        Args:
            project_id: ID du projet
            
        Returns:
            Liste des développeurs membres du projet
        """
        return self.get_project_members(project_id)
    
    def _to_domain_entity(self, user_data: Dict[str, Any]) -> Developer:
        """
        Convertit les données GitLab en entité du domaine Developer.
        
        Args:
            user_data: Données de l'utilisateur provenant de l'API GitLab
            
        Returns:
            Entité Developer correspondante
        """
        # Extraction des données pertinentes
        user_id = str(user_data['id'])
        name = user_data.get('name', '')
        username = user_data.get('username', '')
        email = user_data.get('email', '')
        
        # Dates de création
        created_at = None
        if 'created_at' in user_data:
            try:
                created_at = datetime.fromisoformat(user_data['created_at'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass
        
        # Informations supplémentaires
        metadata = {
            'state': user_data.get('state', ''),
            'avatar_url': user_data.get('avatar_url', ''),
            'web_url': user_data.get('web_url', ''),
            'bio': user_data.get('bio', ''),
            'location': user_data.get('location', ''),
            'is_admin': user_data.get('is_admin', False),
            'is_bot': self._is_bot(user_data),
            'role': user_data.get('role'),
            'role_name': user_data.get('role_name'),
        }
        
        # Création de l'entité Developer
        return Developer(
            id=user_id,
            name=name,
            username=username,
            email=email,
            created_at=created_at,
            metadata=metadata
        )
    
    def _is_bot(self, user_data: Dict[str, Any]) -> bool:
        """
        Détermine si un utilisateur est un bot en se basant sur certains critères.
        
        Args:
            user_data: Données de l'utilisateur
            
        Returns:
            True si l'utilisateur est probablement un bot, False sinon
        """
        # Critères pour identifier un bot
        bot_indicators = [
            'bot' in (user_data.get('username') or '').lower(),
            'bot' in (user_data.get('name') or '').lower(),
            'jenkins' in (user_data.get('username') or '').lower(),
            'jenkins' in (user_data.get('name') or '').lower(),
            'ci' == (user_data.get('username') or '').lower(),
            'gitlab-ci' in (user_data.get('username') or '').lower(),
            'pipeline' in (user_data.get('username') or '').lower(),
            'automation' in (user_data.get('username') or '').lower(),
            'auto' == (user_data.get('username') or '').lower(),
            'system' == (user_data.get('username') or '').lower()
        ]
        
        return any(bot_indicators)
    
    def _get_role_name(self, access_level: Optional[int]) -> str:
        """
        Convertit un niveau d'accès GitLab en nom de rôle.
        
        Args:
            access_level: Niveau d'accès GitLab
            
        Returns:
            Nom du rôle correspondant
        """
        if not access_level:
            return "Unknown"
            
        # Mapping des niveaux d'accès GitLab vers les noms de rôle
        role_mapping = {
            10: "Guest",
            20: "Reporter",
            30: "Developer",
            40: "Maintainer",
            50: "Owner"
        }
        
        return role_mapping.get(access_level, f"Custom ({access_level})")
