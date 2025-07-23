"""
Entités du domaine pour le projet DevOps ETL.

Ce module contient les classes d'entités qui représentent les concepts fondamentaux
du domaine DevOps ETL, indépendamment de toute infrastructure technique.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Set


class Project:
    """
    Représente un projet de développement logiciel.
    
    Cette entité est au cœur du modèle et constitue le point central
    autour duquel les métriques et analyses sont organisées.
    """
    
    def __init__(
        self, 
        id: str, 
        name: str, 
        repository_url: str,
        description: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialise un projet.
        
        Args:
            id: Identifiant unique du projet
            name: Nom du projet
            repository_url: URL du dépôt de code source
            description: Description du projet (optionnel)
            created_at: Date de création du projet (optionnel)
            updated_at: Date de dernière mise à jour du projet (optionnel)
        """
        self.id = id
        self.name = name
        self.repository_url = repository_url
        self.description = description
        self.created_at = created_at
        self.updated_at = updated_at
    
    def __str__(self) -> str:
        return f"Project({self.id}: {self.name})"
    
    def __repr__(self) -> str:
        return self.__str__()


class Developer:
    """
    Représente un développeur travaillant sur un ou plusieurs projets.
    """
    
    def __init__(
        self,
        id: str,
        username: str,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        is_active: bool = True
    ):
        """
        Initialise un développeur.
        
        Args:
            id: Identifiant unique du développeur
            username: Nom d'utilisateur du développeur
            email: Adresse email du développeur (optionnel)
            full_name: Nom complet du développeur (optionnel)
            is_active: Indique si le développeur est actif (par défaut: True)
        """
        self.id = id
        self.username = username
        self.email = email
        self.full_name = full_name
        self.is_active = is_active
    
    def __str__(self) -> str:
        return f"Developer({self.id}: {self.username})"
    
    def __repr__(self) -> str:
        return self.__str__()


class CodeQualityMetric:
    """
    Représente une métrique de qualité de code pour un projet à un moment donné.
    """
    
    def __init__(
        self,
        project_id: str,
        metric_type: str,
        value: float,
        timestamp: datetime,
        source: str,
        raw_data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialise une métrique de qualité de code.
        
        Args:
            project_id: Identifiant du projet auquel la métrique se rapporte
            metric_type: Type de métrique (e.g., "code_coverage", "technical_debt")
            value: Valeur numérique de la métrique
            timestamp: Horodatage de la mesure
            source: Source de la métrique (e.g., "SonarQube", "GitLab")
            raw_data: Données brutes associées à la métrique (optionnel)
        """
        self.project_id = project_id
        self.metric_type = metric_type
        self.value = value
        self.timestamp = timestamp
        self.source = source
        self.raw_data = raw_data or {}
    
    def __str__(self) -> str:
        return f"CodeQualityMetric({self.project_id}, {self.metric_type}: {self.value})"


class Commit:
    """
    Représente un commit dans un projet.
    """
    
    def __init__(
        self,
        id: str,
        project_id: str,
        author_id: str,
        message: str,
        timestamp: datetime,
        stats: Optional[Dict[str, int]] = None
    ):
        """
        Initialise un commit.
        
        Args:
            id: Identifiant unique du commit (hash)
            project_id: Identifiant du projet auquel le commit appartient
            author_id: Identifiant de l'auteur du commit
            message: Message du commit
            timestamp: Horodatage du commit
            stats: Statistiques du commit (e.g., lignes ajoutées/supprimées)
        """
        self.id = id
        self.project_id = project_id
        self.author_id = author_id
        self.message = message
        self.timestamp = timestamp
        self.stats = stats or {"additions": 0, "deletions": 0, "changes": 0}
    
    def __str__(self) -> str:
        return f"Commit({self.id[:8]}, project: {self.project_id}, author: {self.author_id})"


class SecurityVulnerability:
    """
    Représente une vulnérabilité de sécurité détectée dans un projet.
    """
    
    SEVERITY_LEVELS = ["info", "low", "medium", "high", "critical"]
    
    def __init__(
        self,
        id: str,
        project_id: str,
        title: str,
        description: str,
        severity: str,
        detected_at: datetime,
        status: str = "open",
        location: Optional[Dict[str, Any]] = None
    ):
        """
        Initialise une vulnérabilité.
        
        Args:
            id: Identifiant unique de la vulnérabilité
            project_id: Identifiant du projet concerné
            title: Titre de la vulnérabilité
            description: Description de la vulnérabilité
            severity: Niveau de gravité ("info", "low", "medium", "high", "critical")
            detected_at: Date de détection
            status: État actuel ("open", "fixed", "ignored")
            location: Informations sur l'emplacement de la vulnérabilité (optionnel)
        """
        if severity not in self.SEVERITY_LEVELS:
            raise ValueError(f"Severity must be one of {self.SEVERITY_LEVELS}")
            
        self.id = id
        self.project_id = project_id
        self.title = title
        self.description = description
        self.severity = severity
        self.detected_at = detected_at
        self.status = status
        self.location = location or {}
    
    def __str__(self) -> str:
        return f"SecurityVulnerability({self.id}, {self.severity}: {self.title})"
