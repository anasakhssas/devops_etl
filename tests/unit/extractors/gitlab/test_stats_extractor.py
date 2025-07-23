"""
Module de tests unitaires pour GitLabStatsExtractor.

Ce module contient les tests pour la classe GitLabStatsExtractor qui
génère des statistiques à partir des données extraites via la passerelle GitLab.
"""

import json
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from src.extractors.gitlab.gitlab_client import GitLabClient
from src.extractors.gitlab.projects_gateway import GitLabProjectsGateway
from src.extractors.gitlab.stats_extractor import GitLabStatsExtractor


class TestGitLabStatsExtractor:
    """Tests pour la classe GitLabStatsExtractor."""

    @pytest.fixture
    def mock_gateway(self):
        """Fixture pour créer un mock de GitLabProjectsGateway."""
        return MagicMock(spec=GitLabProjectsGateway)

    @pytest.fixture
    def stats_extractor(self, mock_gateway):
        """Fixture pour créer un extracteur de statistiques avec un gateway mocké."""
        return GitLabStatsExtractor(mock_gateway)

    def test_init(self, mock_gateway, stats_extractor):
        """Tester l'initialisation de l'extracteur de statistiques."""
        assert stats_extractor.gateway == mock_gateway

    def test_get_commit_stats(self, stats_extractor, mock_gateway):
        """Tester l'extraction de statistiques de commits."""
        # Configurer le mock pour simuler des commits
        mock_gateway.get_project_commits.return_value = [
            {
                "id": "abc123",
                "author_name": "Dev 1",
                "author_email": "dev1@example.com",
                "created_at": "2023-06-15T10:00:00Z",
                "title": "Fix bug in login form"
            },
            {
                "id": "def456",
                "author_name": "Dev 2",
                "author_email": "dev2@example.com",
                "created_at": "2023-06-15T14:30:00Z",
                "title": "Update README"
            },
            {
                "id": "ghi789",
                "author_name": "Dev 1",
                "author_email": "dev1@example.com",
                "created_at": "2023-06-16T09:15:00Z",
                "title": "Optimize database queries"
            }
        ]

        # Appeler la méthode
        stats = stats_extractor.get_commit_stats(
            project_id=1,
            start_date="2023-06-01",
            end_date="2023-06-30"
        )

        # Vérifier l'appel à la passerelle
        mock_gateway.get_project_commits.assert_called_once_with(
            1,
            params={
                'since': '2023-06-01',
                'until': '2023-06-30',
            }
        )

        # Vérifier les statistiques générées
        assert stats['total_commits'] == 3
        assert 'Dev 1' in stats['authors']
        assert stats['authors']['Dev 1'] == 2
        assert 'Dev 2' in stats['authors']
        assert stats['authors']['Dev 2'] == 1
        assert '2023-06-15' in stats['daily_activity']
        assert stats['daily_activity']['2023-06-15'] == 2
        assert '2023-06-16' in stats['daily_activity']
        assert stats['daily_activity']['2023-06-16'] == 1
        assert stats['avg_commits_per_day'] > 0

    def test_get_commit_stats_with_author_filter(self, stats_extractor, mock_gateway):
        """Tester l'extraction de statistiques de commits avec filtre d'auteur."""
        # Configurer le mock pour simuler des commits
        mock_gateway.get_project_commits.return_value = [
            {
                "id": "abc123",
                "author_name": "Dev 1",
                "author_email": "dev1@example.com",
                "created_at": "2023-06-15T10:00:00Z",
                "title": "Fix bug in login form"
            },
            {
                "id": "def456",
                "author_name": "Dev 2",
                "author_email": "dev2@example.com",
                "created_at": "2023-06-15T14:30:00Z",
                "title": "Update README"
            },
            {
                "id": "ghi789",
                "author_name": "Dev 1",
                "author_email": "dev1@example.com",
                "created_at": "2023-06-16T09:15:00Z",
                "title": "Optimize database queries"
            }
        ]

        # Appeler la méthode avec filtre d'auteur
        stats = stats_extractor.get_commit_stats(
            project_id=1,
            start_date="2023-06-01",
            end_date="2023-06-30",
            author_email="dev1@example.com"
        )

        # Vérifier l'appel à la passerelle
        mock_gateway.get_project_commits.assert_called_once()

        # Vérifier les statistiques générées (seulement Dev 1)
        assert stats['total_commits'] == 2
        assert 'Dev 1' in stats['authors']
        assert stats['authors']['Dev 1'] == 2
        assert 'Dev 2' not in stats['authors']

    def test_get_merge_request_stats(self, stats_extractor, mock_gateway):
        """Tester l'extraction de statistiques de merge requests."""
        # Configurer le mock pour simuler des merge requests
        mock_gateway.get_project_merge_requests.return_value = [
            {
                "id": 123,
                "iid": 1,
                "state": "merged",
                "title": "Feature A",
                "created_at": "2023-06-10T10:00:00Z",
                "merged_at": "2023-06-12T15:00:00Z",
                "user_notes_count": 3,
                "approvals_required": 2,
                "author": {"username": "dev1"},
                "changes_count": 50
            },
            {
                "id": 456,
                "iid": 2,
                "state": "opened",
                "title": "Feature B",
                "created_at": "2023-06-15T09:00:00Z",
                "user_notes_count": 1,
                "approvals_required": 1,
                "author": {"username": "dev2"},
                "changes_count": 120
            },
            {
                "id": 789,
                "iid": 3,
                "state": "closed",
                "title": "Feature C",
                "created_at": "2023-06-20T14:00:00Z",
                "closed_at": "2023-06-21T11:00:00Z",
                "user_notes_count": 5,
                "approvals_required": 2,
                "author": {"username": "dev1"},
                "changes_count": 200
            }
        ]

        # Appeler la méthode
        stats = stats_extractor.get_merge_request_stats(
            project_id=1,
            start_date="2023-06-01",
            end_date="2023-06-30"
        )

        # Vérifier l'appel à la passerelle
        mock_gateway.get_project_merge_requests.assert_called_once_with(
            1,
            params={
                'created_after': '2023-06-01',
                'created_before': '2023-06-30',
            }
        )

        # Vérifier les statistiques générées
        assert stats['total_mrs'] == 3
        assert stats['open_mrs'] == 1
        assert stats['merged_mrs'] == 1
        assert stats['closed_mrs'] == 1
        assert stats['avg_comments'] == 3.0  # (3 + 1 + 5) / 3
        assert stats['mrs_by_author']['dev1'] == 2
        assert stats['mrs_by_author']['dev2'] == 1
        assert stats['avg_time_to_merge'] > 0
        # 50 lignes -> small, 120 -> medium, 200 -> medium-large
        assert stats['size_distribution']['small'] == 1
        assert stats['size_distribution']['medium'] == 1
        assert stats['size_distribution']['large'] == 0
        assert stats['size_distribution']['extra_large'] == 1

    def test_get_issue_stats(self, stats_extractor, mock_gateway):
        """Tester l'extraction de statistiques d'issues."""
        # Configurer le mock pour simuler des issues
        mock_gateway.get_project_issues.return_value = [
            {
                "id": 123,
                "iid": 1,
                "state": "closed",
                "title": "Bug A",
                "created_at": "2023-06-05T10:00:00Z",
                "closed_at": "2023-06-08T15:00:00Z",
                "labels": ["bug", "critical"],
                "author": {"username": "dev1"},
                "assignee": {"username": "dev2"}
            },
            {
                "id": 456,
                "iid": 2,
                "state": "opened",
                "title": "Feature request",
                "created_at": "2023-06-10T09:00:00Z",
                "labels": ["enhancement", "low"],
                "author": {"username": "dev2"}
            },
            {
                "id": 789,
                "iid": 3,
                "state": "closed",
                "title": "Bug B",
                "created_at": "2023-06-15T14:00:00Z",
                "closed_at": "2023-06-16T11:00:00Z",
                "labels": ["bug", "medium"],
                "author": {"username": "dev1"},
                "assignee": {"username": "dev2"}
            }
        ]

        # Appeler la méthode
        stats = stats_extractor.get_issue_stats(
            project_id=1,
            start_date="2023-06-01",
            end_date="2023-06-30"
        )

        # Vérifier l'appel à la passerelle
        mock_gateway.get_project_issues.assert_called_once_with(
            1,
            params={
                'created_after': '2023-06-01',
                'created_before': '2023-06-30',
            }
        )

        # Vérifier les statistiques générées
        assert stats['total_issues'] == 3
        assert stats['open_issues'] == 1
        assert stats['closed_issues'] == 2
        assert stats['avg_time_to_close'] > 0
        assert stats['issues_by_label']['bug'] == 2
        assert stats['issues_by_label']['critical'] == 1
        assert stats['issues_by_author']['dev1'] == 2
        assert stats['issues_by_author']['dev2'] == 1
        assert stats['issues_by_assignee']['dev2'] == 2
        assert stats['priority_distribution']['critical'] == 1
        assert stats['priority_distribution']['medium'] == 1
        assert stats['priority_distribution']['low'] == 1

    def test_get_pipeline_stats(self, stats_extractor, mock_gateway):
        """Tester l'extraction de statistiques de pipelines."""
        # Configurer le mock pour simuler des pipelines
        mock_gateway.get_project_pipelines.return_value = [
            {
                "id": 123,
                "status": "success",
                "ref": "main",
                "created_at": "2023-06-10T10:00:00Z",
                "updated_at": "2023-06-10T10:05:00Z",
                "duration": 300  # 5 minutes en secondes
            },
            {
                "id": 456,
                "status": "failed",
                "ref": "feature-branch",
                "created_at": "2023-06-15T09:00:00Z",
                "updated_at": "2023-06-15T09:02:00Z",
                "duration": 120  # 2 minutes en secondes
            },
            {
                "id": 789,
                "status": "success",
                "ref": "main",
                "created_at": "2023-06-20T14:00:00Z",
                "updated_at": "2023-06-20T14:04:00Z",
                "duration": 240  # 4 minutes en secondes
            },
            {
                "id": 101,
                "status": "running",
                "ref": "develop",
                "created_at": "2023-06-25T11:00:00Z",
                "updated_at": "2023-06-25T11:01:00Z"
            }
        ]

        # Appeler la méthode
        stats = stats_extractor.get_pipeline_stats(
            project_id=1,
            start_date="2023-06-01",
            end_date="2023-06-30"
        )

        # Vérifier l'appel à la passerelle
        mock_gateway.get_project_pipelines.assert_called_once_with(
            1,
            params={
                'updated_after': '2023-06-01',
                'updated_before': '2023-06-30',
            }
        )

        # Vérifier les statistiques générées
        assert stats['total_pipelines'] == 4
        assert stats['status_distribution']['success'] == 2
        assert stats['status_distribution']['failed'] == 1
        assert stats['status_distribution']['running'] == 1
        assert stats['success_rate'] == 2/3 * 100  # 2 succès sur 3 terminés
        assert stats['avg_duration'] == 220  # (300 + 120 + 240) / 3
        assert stats['pipelines_by_ref']['main'] == 2
        assert stats['pipelines_by_ref']['feature-branch'] == 1
        assert stats['pipelines_by_ref']['develop'] == 1
        assert len(stats['weekly_distribution']) > 0  # Au moins une semaine
