"""
Tests unitaires pour la fonctionnalité d'extraction et d'export des utilisateurs GitLab.
Ce module teste spécifiquement la fonction d'identification des bots.
"""
import sys
import os
from pathlib import Path
import unittest
from datetime import datetime, timedelta

# Ajouter le répertoire racine au path pour permettre les imports relatifs
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.append(str(root_dir))

# Import des fonctions à tester
from scripts.export_gitlab_users import identify_bot_accounts

class TestGitLabUsersExport(unittest.TestCase):
    """Tests pour les fonctionnalités d'export des utilisateurs GitLab."""

    def test_identify_bot_accounts_bot_detection(self):
        """Teste la détection des comptes bot."""
        # Créer des exemples de comptes bot
        bot_examples = [
            {"username": "ghost", "name": "Ghost User", "email": "ghost@example.com"},
            {"username": "gitlab-bot", "name": "GitLab Bot", "email": "bot@gitlab.com"},
            {"username": "jenkins-ci", "name": "Jenkins CI", "email": "ci@jenkins.io"},
            {"username": "system", "name": "System", "email": "noreply@gitlab.com"},
            {"username": "user001", "name": "Test User 001", "email": "test001@example.com"},
            {"username": "notification-bot", "name": "Notifications", "email": "no-reply@gitlab.com"},
        ]
        
        # Appeler la fonction à tester
        human_users, bot_users = identify_bot_accounts(bot_examples)
        
        # Vérifier que tous les exemples sont identifiés comme bots
        self.assertEqual(len(bot_users), len(bot_examples), 
                         "Tous les comptes d'exemple devraient être identifiés comme des bots")
        self.assertEqual(len(human_users), 0, 
                         "Aucun compte d'exemple ne devrait être identifié comme humain")

    def test_identify_bot_accounts_human_detection(self):
        """Teste la détection des comptes humains."""
        # Créer des exemples de comptes humains
        human_examples = [
            {"username": "jdupont", "name": "Jean Dupont", "email": "jean.dupont@company.com"},
            {"username": "mmartinez", "name": "Maria Martinez", "email": "m.martinez@company.com"},
            {"username": "elbazi", "name": "EL BAZI MOHAMMED YOUNESS", "email": "elbazi@company.com"},
            {"username": "robert.jenkins", "name": "Robert Jenkins", "email": "r.jenkins@company.com"},
            {"username": "habotier", "name": "Henri Habotier", "email": "h.habotier@company.com"},
        ]
        
        # Appeler la fonction à tester
        human_users, bot_users = identify_bot_accounts(human_examples)
        
        # Vérifier que tous les exemples sont identifiés comme humains
        self.assertEqual(len(human_users), len(human_examples), 
                         "Tous les comptes d'exemple devraient être identifiés comme humains")
        self.assertEqual(len(bot_users), 0, 
                         "Aucun compte d'exemple ne devrait être identifié comme bot")
        
        # Vérifier spécifiquement le cas de EL BAZI qui contient 'bot' dans son nom
        el_bazi = next((u for u in human_users if u["username"] == "elbazi"), None)
        self.assertIsNotNone(el_bazi, "EL BAZI doit être détecté comme humain malgré 'bot' dans son nom")

    def test_identify_bot_accounts_mixed_users(self):
        """Teste la détection avec un mélange de bots et d'humains."""
        # Mélange de comptes bot et humains
        mixed_users = [
            {"username": "ghost", "name": "Ghost User", "email": "ghost@example.com"},  # Bot
            {"username": "jdupont", "name": "Jean Dupont", "email": "jean.dupont@company.com"},  # Humain
            {"username": "gitlab-bot", "name": "GitLab Bot", "email": "bot@gitlab.com"},  # Bot
            {"username": "mmartinez", "name": "Maria Martinez", "email": "m.martinez@company.com"},  # Humain
            {"username": "elbazi", "name": "EL BAZI MOHAMMED YOUNESS", "email": "elbazi@company.com"},  # Humain
        ]
        
        # Appeler la fonction à tester
        human_users, bot_users = identify_bot_accounts(mixed_users)
        
        # Vérifier la répartition
        self.assertEqual(len(human_users), 3, "Trois utilisateurs devraient être identifiés comme humains")
        self.assertEqual(len(bot_users), 2, "Deux utilisateurs devraient être identifiés comme bots")
        
        # Vérifier les usernames des bots
        bot_usernames = [u["username"] for u in bot_users]
        self.assertIn("ghost", bot_usernames, "ghost devrait être identifié comme bot")
        self.assertIn("gitlab-bot", bot_usernames, "gitlab-bot devrait être identifié comme bot")
        
        # Vérifier les usernames des humains
        human_usernames = [u["username"] for u in human_users]
        self.assertIn("jdupont", human_usernames, "jdupont devrait être identifié comme humain")
        self.assertIn("mmartinez", human_usernames, "mmartinez devrait être identifié comme humain")
        self.assertIn("elbazi", human_usernames, "elbazi devrait être identifié comme humain")

    def test_identify_bot_accounts_inactive(self):
        """Teste la détection des comptes bots inactifs."""
        # Date actuelle pour les tests
        now = datetime.now()
        
        # Créer des exemples de comptes avec différentes dates d'activité
        users_with_dates = [
            {
                "username": "old_account", 
                "created_at": (now - timedelta(days=500)).isoformat(), 
                "last_activity_on": None,  # Jamais utilisé
                "email": "old@example.com"
            },  # Bot (créé il y a longtemps, jamais utilisé)
            {
                "username": "recent_account", 
                "created_at": (now - timedelta(days=30)).isoformat(), 
                "last_activity_on": None,  # Jamais utilisé, mais récent
                "email": "recent@example.com"
            },  # Humain (créé récemment)
            {
                "username": "active_account", 
                "created_at": (now - timedelta(days=365)).isoformat(), 
                "last_activity_on": (now - timedelta(days=10)).strftime("%Y-%m-%d"),
                "email": "active@example.com"
            },  # Humain (actif récemment)
        ]
        
        # Appeler la fonction à tester
        human_users, bot_users = identify_bot_accounts(users_with_dates)
        
        # Vérifier les résultats
        self.assertEqual(len(bot_users), 1, "Un compte devrait être identifié comme bot")
        self.assertEqual(len(human_users), 2, "Deux comptes devraient être identifiés comme humains")
        
        # Vérifier si le compte ancien inactif est bien classé comme bot
        bot_usernames = [u["username"] for u in bot_users]
        self.assertIn("old_account", bot_usernames, 
                      "Le vieux compte inactif devrait être identifié comme bot")

if __name__ == '__main__':
    unittest.main()
