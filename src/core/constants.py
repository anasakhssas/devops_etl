"""
Constantes globales pour l'application ETL DevOps.

Ce module définit toutes les constantes utilisées dans l'application,
suivant les conventions de nomenclature PEP 8.
"""

# Configuration par défaut pour les clients API
DEFAULT_API_TIMEOUT = 30
DEFAULT_API_MAX_RETRIES = 3
DEFAULT_API_RETRY_DELAY = 5
DEFAULT_API_ITEMS_PER_PAGE = 100

# Configuration spécifique GitLab
DEFAULT_GITLAB_TIMEOUT = 30
DEFAULT_GITLAB_MAX_RETRIES = 3
DEFAULT_GITLAB_RETRY_DELAY = 5
DEFAULT_GITLAB_ITEMS_PER_PAGE = 100

# Ressources GitLab supportées
SUPPORTED_GITLAB_RESOURCES = [
    "users",
    "projects", 
    "groups",
    "issues",
    "merge_requests",
    "commits",
    "branches",
    "tags"
]

# Colonnes d'export Excel pour GitLab Users
GITLAB_USERS_EXPORT_COLUMNS = [
    {"key": "id", "label": "idUser"},
    {"key": "username", "label": "Username"}, 
    {"key": "name", "label": "FullName"},
    {"key": "email", "label": "Email"},
    {"key": "state", "label": "AccountStatus"},
    {"key": "created_at", "label": "CreatedDate"},
    {"key": "last_activity_on", "label": "LastActivityDate"},
    {"key": "is_admin", "label": "IsAdmin"},
    {"key": "inactivity_days", "label": "InactivityDays"},
    {"key": "data_quality_score", "label": "DataQualityScore"},
    {"key": "web_url", "label": "ProfileUrl"},
    {"key": "account_type", "label": "AccountType"}
]

# Types de comptes utilisateur
USER_ACCOUNT_TYPES = {
    "HUMAN": "Human",
    "BOT": "Bot", 
    "SERVICE": "Service",
    "GHOST": "Ghost"
}

# Indicateurs de détection de bots
BOT_DETECTION_KEYWORDS = [
    "bot",
    "service", 
    "ci",
    "cd",
    "deploy",
    "deployment",
    "automation",
    "system",
    "jenkins",
    "gitlab-ci",
    "runner"
]

# Seuils de qualité des données
DATA_QUALITY_THRESHOLDS = {
    "EXCELLENT": 95,
    "GOOD": 80,
    "ACCEPTABLE": 60,
    "POOR": 40
}

# Seuils d'inactivité (en jours)
INACTIVITY_THRESHOLDS = {
    "RECENT": 30,
    "MODERATE": 90,
    "LONG": 180,
    "VERY_LONG": 365
}

# Formats de date
DATE_FORMATS = {
    "ISO_FORMAT": "%Y-%m-%dT%H:%M:%S.%fZ",
    "DATE_ONLY": "%Y-%m-%d",
    "TIMESTAMP": "%Y-%m-%d--%H%M",
    "DISPLAY": "%d-%m-%Y à %H:%M"
}

# Chemins de fichiers
FILE_PATHS = {
    "OUTPUT_DIR": "data/output",
    "GITLAB_OUTPUT_DIR": "data/output/gitlab",
    "USERS_OUTPUT_DIR": "data/output/gitlab/users",
    "PROJECTS_OUTPUT_DIR": "data/output/gitlab/projects",
    "LOGS_DIR": "logs",
    "CONFIG_DIR": "config",
    "SECRETS_DIR": "config/secrets"
}

# Extensions de fichiers
FILE_EXTENSIONS = {
    "EXCEL": ".xlsx",
    "CSV": ".csv", 
    "JSON": ".json",
    "YAML": ".yaml",
    "LOG": ".log"
}

# Configuration SSL
SSL_CONFIG = {
    "VERIFY_SSL_DEFAULT": True,
    "SSL_WARNING_MESSAGE": (
        "AVERTISSEMENT: La vérification SSL est désactivée. "
        "Cette configuration n'est pas recommandée en production."
    )
}

# Messages d'erreur standardisés
ERROR_MESSAGES = {
    "MISSING_CONFIG": "Configuration manquante pour {parameter}",
    "INVALID_CONFIG": "Configuration invalide pour {parameter}: {value}",
    "CONNECTION_FAILED": "Échec de la connexion à {service}: {error}",
    "AUTHENTICATION_FAILED": "Échec d'authentification à {service}: {error}",
    "API_ERROR": "Erreur API {service}: {error}",
    "RATE_LIMIT_EXCEEDED": "Limite de taux dépassée pour {service}",
    "TIMEOUT_ERROR": "Timeout lors de la connexion à {service}",
    "VALIDATION_ERROR": "Erreur de validation pour {field}: {error}"
}

# Messages de succès standardisés
SUCCESS_MESSAGES = {
    "CONNECTION_ESTABLISHED": "Connexion établie avec succès à {service}",
    "AUTHENTICATION_SUCCESS": "Authentification réussie pour {service}",
    "EXPORT_SUCCESS": "Export réussi: {count} éléments exportés vers {file}",
    "VALIDATION_SUCCESS": "Validation réussie pour {item}",
    "PROCESSING_COMPLETE": "Traitement terminé avec succès"
}

# Configuration des logs
LOG_CONFIG = {
    "DEFAULT_LEVEL": "INFO",
    "DATE_FORMAT": "%Y-%m-%d %H:%M:%S",
    "MESSAGE_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "FILE_FORMAT": "{application}_{level}_{date}.log"
}

# Environnements supportés
SUPPORTED_ENVIRONMENTS = [
    "dev",
    "test", 
    "staging",
    "prod",
    "local"
]

# Configuration des retry
RETRY_CONFIG = {
    "MAX_ATTEMPTS": 3,
    "DELAY_SECONDS": 5,
    "BACKOFF_FACTOR": 2.0,
    "RETRY_ON_ERRORS": [
        "ConnectionError",
        "TimeoutError", 
        "HTTPError"
    ]
}

# Validation des données
VALIDATION_RULES = {
    "EMAIL_REGEX": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    "USERNAME_REGEX": r'^[a-zA-Z0-9._-]+$',
    "URL_REGEX": r'^https?://[^\s/$.?#].[^\s]*$',
    "MIN_PASSWORD_LENGTH": 8,
    "MAX_STRING_LENGTH": 255
}

# Métadonnées d'export
EXPORT_METADATA = {
    "GENERATOR": "ETL DevOps GitLab Exporter",
    "VERSION": "1.0.0",
    "AUTHOR": "DevOps Team",
    "DESCRIPTION": "Export automatisé des données GitLab pour PowerBI"
}

# =============================================================================
# CONSTANTES DE TESTS
# =============================================================================

# Catégories de tests
TEST_CATEGORIES = {
    "UNIT": "unit",
    "INTEGRATION": "integration",
    "FUNCTIONAL": "functional",
    "PERFORMANCE": "performance"
}

# Formats de rapport de tests
TEST_REPORT_FORMATS = {
    "CONSOLE": "console",
    "HTML": "html",
    "JSON": "json",
    "XML": "xml"
}

# Timeouts pour les tests
TEST_TIMEOUTS = {
    "UNIT": 30,      # 30 secondes pour les tests unitaires
    "INTEGRATION": 120,  # 2 minutes pour les tests d'intégration
    "FUNCTIONAL": 300,   # 5 minutes pour les tests fonctionnels
    "PERFORMANCE": 600   # 10 minutes pour les tests de performance
}

# =============================================================================
# CONSTANTES DE SECRETS
# =============================================================================

# Configuration du cache des secrets
SECRET_CACHE_TTL = 3600  # 1 heure en secondes

# Règles de validation des secrets
SECRET_VALIDATION_RULES = {
    "gitlab": {
        "required_fields": ["api_url", "private_token"],
        "format_validation": {
            "api_url": "url",
            "private_token": "token"
        },
        "security_checks": {
            "check_weak_tokens": True,
            "check_insecure_urls": True
        }
    },
    "sonarqube": {
        "required_fields": ["url", "token"],
        "format_validation": {
            "url": "url",
            "token": "token"
        },
        "security_checks": {
            "check_weak_tokens": True,
            "check_insecure_urls": True
        }
    }
}
