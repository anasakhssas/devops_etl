"""
Module pour l'extraction des statistiques des projets GitLab.

Ce module fournit des fonctionnalités pour extraire et analyser
des statistiques sur les projets GitLab: activité des commits,
métriques de pull requests, cycle de vie des issues, etc.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from src.extractors.gitlab.gitlab_client_improved import GitLabClient
from src.extractors.gitlab.projects_gateway import GitLabProjectsGateway


class GitLabStatsExtractor:
    """
    Extracteur de statistiques pour les projets GitLab.
    
    Cette classe fournit des méthodes pour extraire des statistiques
    avancées sur les projets, y compris:
    - Activité de commit (fréquence, volume)
    - Métriques de review (durée moyenne, taux d'approbation)
    - Métriques de cycle de vie des issues (temps de résolution)
    - Métriques de pipeline (taux de succès, durée)
    """
    
    def __init__(self, projects_gateway: GitLabProjectsGateway):
        """
        Initialise l'extracteur avec une passerelle de projets GitLab.
        
        Args:
            projects_gateway: Passerelle permettant l'accès aux projets GitLab.
        """
        self.gateway = projects_gateway
    
    def get_commit_stats(
        self,
        project_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        branch: Optional[str] = None,
        author_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calcule les statistiques d'activité des commits pour un projet.
        
        Args:
            project_id: ID du projet GitLab
            start_date: Date de début au format YYYY-MM-DD (par défaut: 30 jours avant aujourd'hui)
            end_date: Date de fin au format YYYY-MM-DD (par défaut: aujourd'hui)
            branch: Filtrer par branche (optionnel)
            author_email: Filtrer par email d'auteur (optionnel)
            
        Returns:
            Dictionnaire contenant les statistiques:
            - total_commits: Nombre total de commits
            - authors: Liste des auteurs avec leur nombre de commits
            - daily_activity: Répartition des commits par jour
            - avg_commits_per_day: Moyenne des commits par jour
            - lines_changed: Estimation des lignes modifiées
        """
        # Définir les dates par défaut si non spécifiées
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date_obj = datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=30)
            start_date = start_date_obj.strftime('%Y-%m-%d')
        
        # Paramètres de filtrage pour les commits
        params = {
            'since': start_date,
            'until': end_date,
        }
        
        if branch:
            params['ref_name'] = branch
        
        # Récupérer les commits
        commits = self.gateway.get_project_commits(project_id, params=params)
        
        # Filtrer par auteur si spécifié
        if author_email:
            commits = [
                commit for commit in commits 
                if commit.get('author_email', '').lower() == author_email.lower()
            ]
        
        # Initialiser les statistiques
        stats = {
            'total_commits': len(commits),
            'authors': {},
            'daily_activity': {},
            'lines_changed': {
                'additions': 0,
                'deletions': 0,
                'total': 0
            }
        }
        
        # Analyser les commits
        for commit in commits:
            # Compter par auteur
            author = commit.get('author_name', 'Unknown')
            if author not in stats['authors']:
                stats['authors'][author] = 0
            stats['authors'][author] += 1
            
            # Compter par jour
            commit_date = commit.get('created_at', '')[:10]  # YYYY-MM-DD
            if commit_date:
                if commit_date not in stats['daily_activity']:
                    stats['daily_activity'][commit_date] = 0
                stats['daily_activity'][commit_date] += 1
        
        # Calculer la moyenne de commits par jour
        days_count = (datetime.strptime(end_date, '%Y-%m-%d') - 
                     datetime.strptime(start_date, '%Y-%m-%d')).days + 1
        
        stats['avg_commits_per_day'] = stats['total_commits'] / days_count if days_count > 0 else 0
        
        # Trier les auteurs par nombre de commits
        stats['authors'] = dict(
            sorted(stats['authors'].items(), key=lambda x: x[1], reverse=True)
        )
        
        # Trier l'activité quotidienne chronologiquement
        stats['daily_activity'] = dict(
            sorted(stats['daily_activity'].items())
        )
        
        return stats
    
    def get_merge_request_stats(
        self,
        project_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        state: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calcule les statistiques sur les merge requests pour un projet.
        
        Args:
            project_id: ID du projet GitLab
            start_date: Date de début au format YYYY-MM-DD
            end_date: Date de fin au format YYYY-MM-DD
            state: État des MRs (opened, closed, locked, merged)
            
        Returns:
            Dictionnaire contenant les statistiques:
            - total_mrs: Nombre total de merge requests
            - open_mrs: Nombre de MRs ouvertes
            - merged_mrs: Nombre de MRs fusionnées
            - closed_mrs: Nombre de MRs fermées sans fusion
            - avg_time_to_merge: Temps moyen jusqu'à la fusion (en heures)
            - avg_comments: Nombre moyen de commentaires par MR
            - approvals_distribution: Distribution des approbations
        """
        # Paramètres de filtrage pour les merge requests
        params = {}
        
        if start_date:
            params['created_after'] = start_date
        if end_date:
            params['created_before'] = end_date
        if state:
            params['state'] = state
        
        # Récupérer les merge requests
        mrs = self.gateway.get_project_merge_requests(project_id, params=params)
        
        # Initialiser les statistiques
        stats = {
            'total_mrs': len(mrs),
            'open_mrs': 0,
            'merged_mrs': 0,
            'closed_mrs': 0,
            'avg_time_to_merge': 0,
            'avg_comments': 0,
            'approvals_distribution': {},
            'mrs_by_author': {},
            'size_distribution': {
                'small': 0,      # < 100 lignes
                'medium': 0,     # 100-500 lignes
                'large': 0,      # 500-1000 lignes
                'extra_large': 0 # > 1000 lignes
            }
        }
        
        # Variables pour les moyennes
        total_time_to_merge = 0
        total_comments = 0
        merged_count = 0
        
        # Analyser les merge requests
        for mr in mrs:
            # Compter par état
            state = mr.get('state', '')
            if state == 'opened':
                stats['open_mrs'] += 1
            elif state == 'merged':
                stats['merged_mrs'] += 1
                merged_count += 1
                
                # Calculer le temps jusqu'à la fusion
                created_at = mr.get('created_at')
                merged_at = mr.get('merged_at')
                if created_at and merged_at:
                    created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    merged_dt = datetime.fromisoformat(merged_at.replace('Z', '+00:00'))
                    merge_hours = (merged_dt - created_dt).total_seconds() / 3600
                    total_time_to_merge += merge_hours
                
            elif state == 'closed':
                stats['closed_mrs'] += 1
            
            # Compter les commentaires
            discussion_count = mr.get('user_notes_count', 0)
            total_comments += discussion_count
            
            # Compter par nombre d'approbations
            approvals = mr.get('approvals_required', 0)
            if approvals not in stats['approvals_distribution']:
                stats['approvals_distribution'][approvals] = 0
            stats['approvals_distribution'][approvals] += 1
            
            # Compter par auteur
            author = mr.get('author', {}).get('username', 'Unknown')
            if author not in stats['mrs_by_author']:
                stats['mrs_by_author'][author] = 0
            stats['mrs_by_author'][author] += 1
            
            # Classer par taille (nombre de lignes changées)
            changes_count = mr.get('changes_count', 0)
            if changes_count < 100:
                stats['size_distribution']['small'] += 1
            elif changes_count < 500:
                stats['size_distribution']['medium'] += 1
            elif changes_count < 1000:
                stats['size_distribution']['large'] += 1
            else:
                stats['size_distribution']['extra_large'] += 1
        
        # Calculer les moyennes
        if merged_count > 0:
            stats['avg_time_to_merge'] = total_time_to_merge / merged_count
        if stats['total_mrs'] > 0:
            stats['avg_comments'] = total_comments / stats['total_mrs']
        
        # Trier les auteurs par nombre de MRs
        stats['mrs_by_author'] = dict(
            sorted(stats['mrs_by_author'].items(), key=lambda x: x[1], reverse=True)
        )
        
        return stats
    
    def get_issue_stats(
        self,
        project_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        labels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Calcule les statistiques sur les issues pour un projet.
        
        Args:
            project_id: ID du projet GitLab
            start_date: Date de début au format YYYY-MM-DD
            end_date: Date de fin au format YYYY-MM-DD
            labels: Filtrer par labels
            
        Returns:
            Dictionnaire contenant les statistiques:
            - total_issues: Nombre total d'issues
            - open_issues: Nombre d'issues ouvertes
            - closed_issues: Nombre d'issues fermées
            - avg_time_to_close: Temps moyen jusqu'à la fermeture (en heures)
            - issues_by_label: Répartition des issues par label
            - issues_by_author: Répartition des issues par auteur
        """
        # Paramètres de filtrage pour les issues
        params = {}
        
        if start_date:
            params['created_after'] = start_date
        if end_date:
            params['created_before'] = end_date
        if labels:
            params['labels'] = ','.join(labels)
        
        # Récupérer les issues
        issues = self.gateway.get_project_issues(project_id, params=params)
        
        # Initialiser les statistiques
        stats = {
            'total_issues': len(issues),
            'open_issues': 0,
            'closed_issues': 0,
            'avg_time_to_close': 0,
            'issues_by_label': {},
            'issues_by_author': {},
            'issues_by_assignee': {},
            'priority_distribution': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'no_priority': 0
            }
        }
        
        # Variables pour les moyennes
        total_time_to_close = 0
        closed_count = 0
        
        # Analyser les issues
        for issue in issues:
            # Compter par état
            state = issue.get('state', '')
            if state == 'opened':
                stats['open_issues'] += 1
            elif state == 'closed':
                stats['closed_issues'] += 1
                closed_count += 1
                
                # Calculer le temps jusqu'à la fermeture
                created_at = issue.get('created_at')
                closed_at = issue.get('closed_at')
                if created_at and closed_at:
                    created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    closed_dt = datetime.fromisoformat(closed_at.replace('Z', '+00:00'))
                    close_hours = (closed_dt - created_dt).total_seconds() / 3600
                    total_time_to_close += close_hours
            
            # Compter par label
            issue_labels = issue.get('labels', [])
            for label in issue_labels:
                if label not in stats['issues_by_label']:
                    stats['issues_by_label'][label] = 0
                stats['issues_by_label'][label] += 1
                
                # Détection de priorité basée sur les labels
                if 'critical' in label.lower():
                    stats['priority_distribution']['critical'] += 1
                elif 'high' in label.lower() or 'important' in label.lower():
                    stats['priority_distribution']['high'] += 1
                elif 'medium' in label.lower() or 'normal' in label.lower():
                    stats['priority_distribution']['medium'] += 1
                elif 'low' in label.lower() or 'minor' in label.lower():
                    stats['priority_distribution']['low'] += 1
            
            # Si aucune priorité détectée
            if not any(p in [l.lower() for l in issue_labels] for p in ['critical', 'high', 'medium', 'low', 'important', 'normal', 'minor']):
                stats['priority_distribution']['no_priority'] += 1
            
            # Compter par auteur
            author = issue.get('author', {}).get('username', 'Unknown')
            if author not in stats['issues_by_author']:
                stats['issues_by_author'][author] = 0
            stats['issues_by_author'][author] += 1
            
            # Compter par assigné
            assignee = issue.get('assignee', {}).get('username', 'Unassigned')
            if assignee != 'Unassigned':
                if assignee not in stats['issues_by_assignee']:
                    stats['issues_by_assignee'][assignee] = 0
                stats['issues_by_assignee'][assignee] += 1
        
        # Calculer les moyennes
        if closed_count > 0:
            stats['avg_time_to_close'] = total_time_to_close / closed_count
        
        # Trier les issues par label
        stats['issues_by_label'] = dict(
            sorted(stats['issues_by_label'].items(), key=lambda x: x[1], reverse=True)
        )
        
        # Trier les issues par auteur
        stats['issues_by_author'] = dict(
            sorted(stats['issues_by_author'].items(), key=lambda x: x[1], reverse=True)
        )
        
        # Trier les issues par assigné
        stats['issues_by_assignee'] = dict(
            sorted(stats['issues_by_assignee'].items(), key=lambda x: x[1], reverse=True)
        )
        
        return stats
    
    def get_pipeline_stats(
        self,
        project_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        ref: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calcule les statistiques sur les pipelines pour un projet.
        
        Args:
            project_id: ID du projet GitLab
            start_date: Date de début au format YYYY-MM-DD
            end_date: Date de fin au format YYYY-MM-DD
            ref: Nom de la branche/référence
            
        Returns:
            Dictionnaire contenant les statistiques:
            - total_pipelines: Nombre total de pipelines
            - status_distribution: Répartition par statut
            - success_rate: Taux de réussite (%)
            - avg_duration: Durée moyenne des pipelines (en secondes)
            - pipelines_by_ref: Répartition par référence/branche
        """
        # Paramètres de filtrage pour les pipelines
        params = {}
        
        if start_date:
            params['updated_after'] = start_date
        if end_date:
            params['updated_before'] = end_date
        if ref:
            params['ref'] = ref
        
        # Récupérer les pipelines
        pipelines = self.gateway.get_project_pipelines(project_id, params=params)
        
        # Initialiser les statistiques
        stats = {
            'total_pipelines': len(pipelines),
            'status_distribution': {
                'success': 0,
                'failed': 0,
                'canceled': 0,
                'running': 0,
                'pending': 0,
                'skipped': 0,
                'other': 0
            },
            'success_rate': 0,
            'avg_duration': 0,
            'pipelines_by_ref': {},
            'weekly_distribution': {}
        }
        
        # Variables pour les moyennes
        total_duration = 0
        completed_pipelines = 0
        
        # Analyser les pipelines
        for pipeline in pipelines:
            # Compter par statut
            status = pipeline.get('status', 'other')
            if status in stats['status_distribution']:
                stats['status_distribution'][status] += 1
            else:
                stats['status_distribution']['other'] += 1
                
            # Compter comme complété si succès ou échec (pas annulé ou en cours)
            if status in ['success', 'failed']:
                completed_pipelines += 1
                
                # Calculer la durée
                if 'duration' in pipeline and pipeline['duration']:
                    total_duration += pipeline['duration']
            
            # Compter par référence/branche
            ref_name = pipeline.get('ref', 'Unknown')
            if ref_name not in stats['pipelines_by_ref']:
                stats['pipelines_by_ref'][ref_name] = 0
            stats['pipelines_by_ref'][ref_name] += 1
            
            # Regrouper par semaine
            created_at = pipeline.get('created_at')
            if created_at:
                created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                week_start = (created_dt - timedelta(days=created_dt.weekday())).strftime('%Y-%m-%d')
                
                if week_start not in stats['weekly_distribution']:
                    stats['weekly_distribution'][week_start] = {
                        'total': 0,
                        'success': 0,
                        'failed': 0,
                        'other': 0
                    }
                
                stats['weekly_distribution'][week_start]['total'] += 1
                if status == 'success':
                    stats['weekly_distribution'][week_start]['success'] += 1
                elif status == 'failed':
                    stats['weekly_distribution'][week_start]['failed'] += 1
                else:
                    stats['weekly_distribution'][week_start]['other'] += 1
        
        # Calculer le taux de réussite
        if completed_pipelines > 0:
            stats['success_rate'] = (stats['status_distribution']['success'] / completed_pipelines) * 100
            
        # Calculer la durée moyenne
        if completed_pipelines > 0:
            stats['avg_duration'] = total_duration / completed_pipelines
        
        # Trier les pipelines par référence
        stats['pipelines_by_ref'] = dict(
            sorted(stats['pipelines_by_ref'].items(), key=lambda x: x[1], reverse=True)
        )
        
        # Trier la distribution hebdomadaire chronologiquement
        stats['weekly_distribution'] = dict(
            sorted(stats['weekly_distribution'].items())
        )
        
        return stats
