"""
Tests unitaires pour la nouvelle implémentation avec python-gitlab.
"""
import sys
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
import gitlab
from datetime import datetime

# Ajouter le répertoire racine au path pour permettre les imports relatifs
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

# Import des fonctions à tester avec la nouvelle implémentation
from scripts.gitlab_users_export import identify_bot_accounts

class TestGitLabPythonGitlabImplementation(unittest.TestCase):
    """Tests pour la nouvelle implémentation avec python-gitlab."""

    def test_identify_bot_accounts_with_gitlab_objects(self):
        """Test de la fonction d'identification des bots avec des objets GitLab."""
        
        # Créer des mocks d'objets GitLab User
        mock_users = []
        
        # Créer un mock d'utilisateur humain normal
        human_user = MagicMock()
        human_user.username = 'jdupont'
        human_user.name = 'Jean Dupont'
        human_user.email = 'jean.dupont@company.com'
        human_user.bot = False
        human_user.service_account = False
        human_user.attributes = {
            'username': 'jdupont',
            'name': 'Jean Dupont',
            'email': 'jean.dupont@company.com',
            'bot': False,
            'service_account': False
        }
        mock_users.append(human_user)
        
        # Créer un mock d'utilisateur Bot (avec flag bot explicite)
        bot_user = MagicMock()
        bot_user.username = 'gitlab-bot'
        bot_user.name = 'GitLab Bot'
        bot_user.email = 'bot@gitlab.com'
        bot_user.bot = True
        bot_user.service_account = False
        bot_user.attributes = {
            'username': 'gitlab-bot',
            'name': 'GitLab Bot',
            'email': 'bot@gitlab.com',
            'bot': True,
            'service_account': False
        }
        mock_users.append(bot_user)
        
        # Créer un mock d'utilisateur de service
        service_user = MagicMock()
        service_user.username = 'ci-service'
        service_user.name = 'CI Service'
        service_user.email = 'ci@service.com'
        service_user.bot = False
        service_user.service_account = True
        service_user.attributes = {
            'username': 'ci-service',
            'name': 'CI Service',
            'email': 'ci@service.com',
            'bot': False,
            'service_account': True
        }
        mock_users.append(service_user)
        
        # Créer un mock pour le cas spécial EL BAZI
        el_bazi_user = MagicMock()
        el_bazi_user.username = 'elbazi'
        el_bazi_user.name = 'EL BAZI MOHAMMED YOUNESS'
        el_bazi_user.email = 'elbazi@company.com'
        el_bazi_user.bot = False  # Non marqué comme bot
        el_bazi_user.service_account = False
        el_bazi_user.attributes = {
            'username': 'elbazi',
            'name': 'EL BAZI MOHAMMED YOUNESS',
            'email': 'elbazi@company.com',
            'bot': False,
            'service_account': False
        }
        mock_users.append(el_bazi_user)
        
        # Créer un mock pour Ghost User
        ghost_user = MagicMock()
        ghost_user.username = 'ghost'
        ghost_user.name = 'Ghost User'
        ghost_user.email = None
        ghost_user.bot = True  # Marqué comme bot
        ghost_user.service_account = False
        ghost_user.attributes = {
            'username': 'ghost',
            'name': 'Ghost User',
            'email': None,
            'bot': True,
            'service_account': False
        }
        mock_users.append(ghost_user)
        
        # Appeler la fonction à tester
        human_users, bot_users = identify_bot_accounts(mock_users)
        
        # Vérifier les résultats
        self.assertEqual(len(human_users), 2, "Devrait y avoir 2 utilisateurs humains (Jean Dupont et EL BAZI)")
        self.assertEqual(len(bot_users), 3, "Devrait y avoir 3 bots (gitlab-bot, ci-service, ghost)")
        
        # Vérifier que EL BAZI est bien classé comme humain malgré 'bot' dans son nom
        human_usernames = [user.get('username', '') for user in human_users]
        self.assertIn('elbazi', human_usernames, "EL BAZI doit être classé comme humain")
        
        # Vérifier que les bots sont correctement identifiés
        bot_usernames = [user.get('username', '') for user in bot_users]
        self.assertIn('gitlab-bot', bot_usernames, "gitlab-bot doit être classé comme bot")
        self.assertIn('ci-service', bot_usernames, "ci-service doit être classé comme bot")
        self.assertIn('ghost', bot_usernames, "ghost doit être classé comme bot")

if __name__ == '__main__':
    unittest.main()
