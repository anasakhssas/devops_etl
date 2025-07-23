"""
Objets de valeur (Value Objects) pour le domaine DevOps ETL.

Ce module contient des classes immuables représentant des concepts
du domaine qui sont définis par leurs attributs plutôt que par une identité.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set, FrozenSet, Tuple
from dataclasses import dataclass, field


@dataclass(frozen=True)
class DateRange:
    """
    Représente une période entre deux dates.
    
    Cet objet de valeur est immuable et utilisé pour définir des fenêtres temporelles
    pour l'analyse des données.
    """
    start_date: datetime
    end_date: datetime
    
    def __post_init__(self):
        """Valide que la date de fin est après la date de début."""
        if self.end_date < self.start_date:
            raise ValueError("La date de fin doit être postérieure à la date de début")
    
    @property
    def duration(self) -> timedelta:
        """Retourne la durée de la période."""
        return self.end_date - self.start_date
    
    def contains(self, date: datetime) -> bool:
        """Vérifie si une date est dans la période."""
        return self.start_date <= date <= self.end_date
        
    @classmethod
    def last_n_days(cls, n: int, end_date: Optional[datetime] = None) -> 'DateRange':
        """
        Crée une période des n derniers jours jusqu'à end_date (aujourd'hui par défaut).
        
        Cette méthode de commodité permet de générer rapidement une période
        représentant les n derniers jours sans avoir à manipuler directement les dates.
        
        Args:
            n: Nombre de jours dans la période
            end_date: Date de fin (aujourd'hui par défaut)
            
        Returns:
            Une instance de DateRange
            
        Examples:
            >>> # Créer une période des 7 derniers jours
            >>> period = DateRange.last_n_days(7)
            >>> # Créer une période des 30 derniers jours jusqu'au 2025-01-01
            >>> period = DateRange.last_n_days(30, datetime(2025, 1, 1))
        """
        end = end_date or datetime.now()
        start = end - timedelta(days=n)
        return cls(start, end)


@dataclass(frozen=True)
class CommitActivity:
    """
    Représente l'activité de commits sur une période donnée.
    """
    period: DateRange
    count: int
    authors: FrozenSet[str] = field(default_factory=frozenset)
    additions: int = 0
    deletions: int = 0
    file_count: int = 0
    
    @property
    def author_count(self) -> int:
        """Retourne le nombre d'auteurs uniques."""
        return len(self.authors)
    
    @property
    def net_changes(self) -> int:
        """Retourne le nombre net de changements (additions - deletions)."""
        return self.additions - self.deletions
    
    @property
    def total_changes(self) -> int:
        """Retourne le nombre total de changements (additions + deletions)."""
        return self.additions + self.deletions
        
    @property
    def average_changes_per_commit(self) -> float:
        """
        Retourne la moyenne des changements par commit.
        
        Cette métrique permet d'évaluer la taille moyenne des commits et
        peut être utile pour identifier des tendances dans les pratiques de développement.
        Une valeur élevée peut indiquer des commits trop volumineux.
        
        Returns:
            Le nombre moyen de changements (additions + suppressions) par commit
            ou 0.0 si aucun commit n'est présent
        """
        if self.count == 0:
            return 0.0
        return self.total_changes / self.count
        
    @property
    def average_changes_per_file(self) -> float:
        """
        Retourne la moyenne des changements par fichier.
        
        Cette métrique permet d'évaluer la concentration des modifications
        et peut aider à identifier les fichiers qui subissent d'importantes modifications.
        
        Returns:
            Le nombre moyen de changements par fichier modifié
            ou 0.0 si aucun fichier n'est présent
        """
        if self.file_count == 0:
            return 0.0
        return self.total_changes / self.file_count


@dataclass(frozen=True)
class MetricValue:
    """
    Représente une valeur métrique avec son contexte.
    """
    name: str
    value: float
    unit: str = ""
    timestamp: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)
    source: str = "manual"  # Source de la métrique (sonarqube, gitlab, etc.)
    
    def __str__(self) -> str:
        unit_str = f" {self.unit}" if self.unit else ""
        return f"{self.value}{unit_str}"
        
    def is_valid(self) -> bool:
        """
        Vérifie si la valeur métrique est valide selon des règles basiques.
        
        Cette méthode applique plusieurs règles de validation en fonction de l'unité:
        - Les pourcentages doivent être entre 0 et 100
        - Les compteurs et ratios ne peuvent pas être négatifs
        - D'autres validations spécifiques peuvent être ajoutées selon les besoins
        
        La validation est importante pour garantir l'intégrité des données
        avant de les utiliser dans des calculs ou des rapports.
        
        Returns:
            True si la métrique est valide selon les règles définies, False sinon
        """
        # Vérifie les valeurs négatives pour certaines unités qui ne devraient pas l'être
        if self.value < 0 and self.unit in ('%', 'count', 'ratio'):
            return False
            
        # Vérifie que les pourcentages sont entre 0 et 100
        if self.unit == '%' and (self.value < 0 or self.value > 100):
            return False
            
        return True


@dataclass(frozen=True)
class CodeCoverage:
    """
    Représente la couverture de code d'un projet.
    """
    line_coverage: float  # Pourcentage de lignes couvertes (0-100)
    branch_coverage: float  # Pourcentage de branches couvertes (0-100)
    covered_lines: int
    total_lines: int
    covered_branches: int = 0
    total_branches: int = 0
    timestamp: Optional[datetime] = None
    source: str = "sonarqube"  # Source des données de couverture
    
    def __post_init__(self):
        """Valide que les pourcentages sont entre 0 et 100."""
        object.__setattr__(self, "line_coverage", max(0, min(100, self.line_coverage)))
        object.__setattr__(self, "branch_coverage", max(0, min(100, self.branch_coverage)))
    
    @property
    def overall_coverage(self) -> float:
        """Calcule la couverture globale (moyenne pondérée ligne/branche)."""
        if self.total_branches == 0:
            return self.line_coverage
        
        # Moyenne pondérée 70% ligne, 30% branche
        return 0.7 * self.line_coverage + 0.3 * self.branch_coverage
        
    @property
    def coverage_rating(self) -> str:
        """
        Retourne une note de couverture (A-E) selon les seuils SonarQube.
        
        Cette propriété convertit le pourcentage de couverture en une note
        alphabétique similaire à celle utilisée par SonarQube, facilitant
        l'interprétation rapide de la qualité de la couverture de tests.
        
        Les seuils utilisés sont:
        - A: >= 80% (Excellent)
        - B: >= 70% (Bon)
        - C: >= 50% (Acceptable)
        - D: >= 30% (Insuffisant)
        - E: < 30% (Critique)
        
        Returns:
            Une lettre entre A et E représentant la qualité de la couverture
        """
        coverage = self.overall_coverage
        if coverage >= 80:
            return "A"
        elif coverage >= 70:
            return "B"
        elif coverage >= 50:
            return "C"
        elif coverage >= 30:
            return "D"
        else:
            return "E"


@dataclass(frozen=True)
class TechnicalDebt:
    """
    Représente la dette technique d'un projet.
    """
    effort_days: float  # Effort estimé en jours pour résoudre la dette
    issues_count: int  # Nombre total de problèmes détectés
    blocker_issues: int = 0
    critical_issues: int = 0
    major_issues: int = 0
    minor_issues: int = 0
    info_issues: int = 0
    code_smells: int = 0
    timestamp: Optional[datetime] = None
    source: str = "sonarqube"
    
    @property
    def weighted_issues(self) -> float:
        """Calcule un score pondéré basé sur la gravité des problèmes."""
        return (
            10 * self.blocker_issues +
            5 * self.critical_issues +
            3 * self.major_issues +
            1 * self.minor_issues +
            0.1 * self.info_issues
        )
        
    @property
    def technical_debt_ratio(self) -> float:
        """
        Calcule le ratio de dette technique par rapport au total des problèmes.
        
        Ce ratio permet d'évaluer la gravité moyenne des problèmes détectés
        dans le code. Une valeur plus élevée indique une concentration de problèmes 
        plus graves, ce qui peut nécessiter une attention prioritaire.
        
        La formule utilisée est:
            weighted_issues / issues_count
            
        où weighted_issues est la somme pondérée des problèmes selon leur gravité.
        
        Returns:
            Le ratio de dette technique, ou 0.0 si aucun problème n'est détecté
        """
        if self.issues_count == 0:
            return 0.0
        
        return self.weighted_issues / self.issues_count
        
    @property
    def debt_rating(self) -> str:
        """
        Retourne une note (A-E) basée sur l'effort en jours.
        
        A: < 5 jours, B: < 10 jours, C: < 20 jours, D: < 40 jours, E: >= 40 jours
        """
        if self.effort_days < 5:
            return "A"
        elif self.effort_days < 10:
            return "B"
        elif self.effort_days < 20:
            return "C"
        elif self.effort_days < 40:
            return "D"
        else:
            return "E"


@dataclass(frozen=True)
class ProjectIdentifier:
    """
    Identifiant de projet normalisé qui peut faire référence à un projet
    dans différents systèmes.
    """
    name: str  # Nom normalisé du projet
    gitlab_id: Optional[str] = None
    sonarqube_key: Optional[str] = None
    defect_dojo_id: Optional[str] = None
    dependency_track_id: Optional[str] = None
    jira_key: Optional[str] = None
    organization: Optional[str] = None
    
    def __str__(self) -> str:
        return self.name
        
    def has_quality_tracking(self) -> bool:
        """
        Détermine si le projet est tracé dans les outils de qualité.
        
        Cette méthode vérifie si le projet est configuré pour le suivi
        de la qualité du code via des outils comme SonarQube.
        
        Returns:
            True si le projet dispose d'une clé SonarQube, False sinon
        """
        return bool(self.sonarqube_key)
        
    def has_security_tracking(self) -> bool:
        """
        Détermine si le projet est tracé dans les outils de sécurité.
        
        Cette méthode vérifie si le projet est configuré pour le suivi
        des vulnérabilités de sécurité via des outils comme DefectDojo 
        ou Dependency Track.
        
        Returns:
            True si le projet dispose d'identifiants dans les outils de sécurité, False sinon
        """
        return bool(self.defect_dojo_id or self.dependency_track_id)
        
    @classmethod
    def from_gitlab_project(cls, gitlab_project: Dict[str, Any]) -> 'ProjectIdentifier':
        """
        Crée un identifiant de projet à partir des données d'un projet GitLab.
        
        Cette méthode de fabrique facilite la création d'un identifiant normalisé
        à partir des données brutes d'un projet GitLab. Elle extrait automatiquement
        les informations pertinentes comme le nom du projet, son ID et son organisation.
        
        Args:
            gitlab_project: Dictionnaire contenant les données du projet GitLab
                Doit contenir au minimum 'id' et idéalement 'path_with_namespace'
                et 'namespace.name'
            
        Returns:
            Un nouvel identifiant de projet configuré avec les données GitLab
            
        Examples:
            >>> project_data = {'id': 123, 'path_with_namespace': 'acme/api-service', 
            ...                'namespace': {'name': 'acme'}}
            >>> project_id = ProjectIdentifier.from_gitlab_project(project_data)
            >>> print(project_id.name)
            'api-service'
        """
        name = gitlab_project.get('path_with_namespace', '').split('/')[-1]
        return cls(
            name=name,
            gitlab_id=str(gitlab_project.get('id')),
            organization=gitlab_project.get('namespace', {}).get('name')
        )
