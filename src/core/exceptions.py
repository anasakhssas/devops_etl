"""
Module définissant les exceptions personnalisées pour le système ETL.
"""

class ETLException(Exception):
    """Exception de base pour toutes les erreurs spécifiques à l'ETL."""
    pass


class ConfigurationError(ETLException):
    """Erreur liée à la configuration."""
    pass


class ExtractionError(ETLException):
    """Erreur survenue pendant l'extraction des données."""
    pass


class APIConnectionError(ExtractionError):
    """Erreur de connexion à une API."""
    pass


class APIAuthenticationError(APIConnectionError):
    """Erreur d'authentification à une API."""
    pass


class APIRateLimitError(APIConnectionError):
    """Limite de taux d'une API atteinte."""
    pass


class TransformationError(ETLException):
    """Erreur survenue pendant la transformation des données."""
    pass


class ValidationError(ETLException):
    """Erreur survenue pendant la validation des données."""
    pass


class LoadError(ETLException):
    """Erreur survenue pendant le chargement des données."""
    pass


class SecurityError(ETLException):
    """Erreur liée à la sécurité ou aux permissions."""
    pass


class DataIntegrityError(ETLException):
    """Erreur liée à l'intégrité des données."""
    pass


class ResourceNotFoundError(ETLException):
    """Erreur lorsqu'une ressource demandée n'est pas trouvée."""
    pass


class DependencyError(ETLException):
    """Erreur liée à une dépendance externe."""
    pass
