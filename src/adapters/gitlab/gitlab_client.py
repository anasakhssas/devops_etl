"""
Client GitLab pour accéder à l'API GitLab.

Ce module contient l'implémentation d'un client GitLab réutilisable par les différents 
repositories. Il encapsule toute la logique d'accès à l'API GitLab.
"""

import time
import logging
from typing import Any, Dict, List, Optional, Union, cast
from urllib.parse import urljoin

import gitlab
import requests
from gitlab.exceptions import GitlabAuthenticationError, GitlabError

from src.domain.ports.services import LoggingService, LogLevel


class GitLabClient:
    """Client pour interagir avec l'API GitLab."""
    
    def __init__(
        self, 
        url: str, 
        token: str,
        logger: Optional[LoggingService] = None,
        timeout: int = 30,
        retry_count: int = 3,
        retry_delay: float = 1.0,
        ssl_verify: bool = True
    ):
        """
        Initialise un nouveau client GitLab.
        
        Args:
            url: URL de l'instance GitLab
            token: Jeton d'accès à l'API
            logger: Service de logging (optionnel)
            timeout: Délai d'expiration des requêtes en secondes
            retry_count: Nombre de tentatives en cas d'échec
            retry_delay: Délai initial entre les tentatives (augmente exponentiellement)
            ssl_verify: Valider les certificats SSL
        """
        self.url = url
        self.token = token
        self.logger = logger
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.ssl_verify = ssl_verify
        self._gl = None
        
    @property
    def gl(self) -> gitlab.Gitlab:
        """
        Retourne une instance configurée du client GitLab.
        
        Initialise la connexion si nécessaire.
        
        Returns:
            Instance connectée du client GitLab
        """
        if self._gl is None:
            self._connect()
        return self._gl
    
    def _connect(self) -> None:
        """
        Établit la connexion avec l'API GitLab.
        
        Raises:
            ConnectionError: En cas d'échec de connexion après toutes les tentatives
        """
        for attempt in range(self.retry_count):
            try:
                self._log(LogLevel.INFO, f"Tentative de connexion à GitLab ({attempt+1}/{self.retry_count})")
                self._gl = gitlab.Gitlab(
                    url=self.url,
                    private_token=self.token,
                    ssl_verify=self.ssl_verify,
                    timeout=self.timeout
                )
                self._gl.auth()
                self._log(LogLevel.INFO, "Connexion à GitLab établie avec succès")
                return
            except GitlabAuthenticationError as e:
                # Erreur d'authentification, inutile de réessayer
                self._log(LogLevel.ERROR, f"Erreur d'authentification GitLab: {str(e)}")
                raise ConnectionError(f"Erreur d'authentification GitLab: {str(e)}")
            except (GitlabError, requests.RequestException) as e:
                if attempt == self.retry_count - 1:
                    # Dernière tentative échouée
                    self._log(LogLevel.ERROR, f"Échec de connexion à GitLab après {self.retry_count} tentatives: {str(e)}")
                    raise ConnectionError(f"Échec de connexion à GitLab: {str(e)}")
                else:
                    # Attendre avant de réessayer (backoff exponentiel)
                    delay = self.retry_delay * (2 ** attempt)
                    self._log(LogLevel.WARNING, f"Échec de connexion, nouvelle tentative dans {delay:.2f}s: {str(e)}")
                    time.sleep(delay)
    
    def _log(self, level: LogLevel, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Enregistre un message dans les logs.
        
        Args:
            level: Niveau de log
            message: Message à enregistrer
            context: Contexte additionnel
        """
        if self.logger:
            self.logger.log(level, message, context)
        elif level in (LogLevel.ERROR, LogLevel.CRITICAL):
            logging.error(message)
        elif level == LogLevel.WARNING:
            logging.warning(message)
        elif level == LogLevel.INFO:
            logging.info(message)
        elif level == LogLevel.DEBUG:
            logging.debug(message)
    
    def get_projects(self, search: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Récupère la liste des projets.
        
        Args:
            search: Filtre de recherche sur le nom du projet
            **kwargs: Paramètres de filtrage supplémentaires
            
        Returns:
            Liste des projets
        """
        try:
            params = {'simple': True, 'per_page': 100}
            if search:
                params['search'] = search
            
            params.update(kwargs)
            projects_list = self.gl.projects.list(**params)
            
            # Convertir en liste de dictionnaires
            return [self._to_dict(project) for project in projects_list]
        except (GitlabError, requests.RequestException) as e:
            self._log(LogLevel.ERROR, f"Erreur lors de la récupération des projets: {str(e)}")
            raise
    
    def get_project(self, project_id: Union[int, str]) -> Dict[str, Any]:
        """
        Récupère les détails d'un projet par son ID.
        
        Args:
            project_id: ID ou chemin du projet (namespace/project)
            
        Returns:
            Détails du projet
            
        Raises:
            ValueError: Si le projet n'est pas trouvé
        """
        try:
            project = self.gl.projects.get(project_id)
            return self._to_dict(project)
        except gitlab.exceptions.GitlabGetError as e:
            self._log(LogLevel.ERROR, f"Erreur lors de la récupération du projet {project_id}: {str(e)}")
            raise ValueError(f"Projet {project_id} non trouvé")
        except (GitlabError, requests.RequestException) as e:
            self._log(LogLevel.ERROR, f"Erreur lors de la récupération du projet {project_id}: {str(e)}")
            raise
    
    def get_project_members(self, project_id: Union[int, str]) -> List[Dict[str, Any]]:
        """
        Récupère la liste des membres d'un projet.
        
        Args:
            project_id: ID ou chemin du projet
            
        Returns:
            Liste des membres du projet
        """
        try:
            project = self.gl.projects.get(project_id)
            members = project.members.all(all=True)
            return [self._to_dict(member) for member in members]
        except (GitlabError, requests.RequestException) as e:
            self._log(LogLevel.ERROR, f"Erreur lors de la récupération des membres du projet {project_id}: {str(e)}")
            raise
    
    def get_user(self, user_id: Union[int, str]) -> Dict[str, Any]:
        """
        Récupère les détails d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Détails de l'utilisateur
        """
        try:
            user = self.gl.users.get(user_id)
            return self._to_dict(user)
        except (GitlabError, requests.RequestException) as e:
            self._log(LogLevel.ERROR, f"Erreur lors de la récupération de l'utilisateur {user_id}: {str(e)}")
            raise
    
    def get_users(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Récupère la liste des utilisateurs.
        
        Args:
            **kwargs: Paramètres de filtrage
            
        Returns:
            Liste des utilisateurs
        """
        try:
            params = {'per_page': 100}
            params.update(kwargs)
            users = self.gl.users.list(**params)
            return [self._to_dict(user) for user in users]
        except (GitlabError, requests.RequestException) as e:
            self._log(LogLevel.ERROR, f"Erreur lors de la récupération des utilisateurs: {str(e)}")
            raise
    
    def get_commits(self, project_id: Union[int, str], since: Optional[str] = None, until: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Récupère la liste des commits d'un projet.
        
        Args:
            project_id: ID ou chemin du projet
            since: Date de début (format ISO)
            until: Date de fin (format ISO)
            **kwargs: Paramètres de filtrage supplémentaires
            
        Returns:
            Liste des commits
        """
        try:
            project = self.gl.projects.get(project_id)
            
            params = {'per_page': 100}
            if since:
                params['since'] = since
            if until:
                params['until'] = until
            params.update(kwargs)
            
            commits = project.commits.list(**params)
            return [self._to_dict(commit) for commit in commits]
        except (GitlabError, requests.RequestException) as e:
            self._log(LogLevel.ERROR, f"Erreur lors de la récupération des commits du projet {project_id}: {str(e)}")
            raise
    
    def get_commit_stats(self, project_id: Union[int, str], since: Optional[str] = None, until: Optional[str] = None) -> Dict[str, Any]:
        """
        Récupère des statistiques agrégées sur les commits d'un projet.
        
        Args:
            project_id: ID ou chemin du projet
            since: Date de début (format ISO)
            until: Date de fin (format ISO)
            
        Returns:
            Statistiques agrégées des commits
        """
        commits = self.get_commits(project_id, since, until)
        
        # Extraction des statistiques
        total_commits = len(commits)
        authors = set()
        total_additions = 0
        total_deletions = 0
        
        for commit in commits:
            if 'author_email' in commit:
                authors.add(commit['author_email'])
            
            # Récupération des statistiques détaillées du commit si disponibles
            if 'stats' in commit:
                total_additions += commit['stats'].get('additions', 0)
                total_deletions += commit['stats'].get('deletions', 0)
        
        return {
            'total_commits': total_commits,
            'unique_authors': len(authors),
            'authors': list(authors),
            'total_additions': total_additions,
            'total_deletions': total_deletions,
            'net_changes': total_additions - total_deletions
        }
    
    def _to_dict(self, obj: Any) -> Dict[str, Any]:
        """
        Convertit un objet GitLab en dictionnaire.
        
        Args:
            obj: Objet GitLab à convertir
            
        Returns:
            Dictionnaire contenant les attributs de l'objet
        """
        # Si l'objet a déjà une méthode to_dict(), l'utiliser
        if hasattr(obj, 'attributes'):
            return obj.attributes
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        # Sinon, créer un dictionnaire à partir des attributs accessibles
        elif hasattr(obj, '__dict__'):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        # En dernier recours, retourner l'objet tel quel
        return obj
