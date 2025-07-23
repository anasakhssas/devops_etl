"""
Configuration centralisée et gestionnaire de configuration pour l'application DevOps ETL.

Ce module fournit des constantes, configurations par défaut et un gestionnaire
de configuration unifié pour assurer la cohérence à travers l'application.

Version optimisée avec les meilleures pratiques :
- Configuration centralisée
- Validation des paramètres
- Chemins standardisés
- Constantes globales
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml

# ================================
# CONSTANTES GLOBALES
# ================================

# Chemins de l'application
BASE_DIR = Path(__file__).parent.parent.parent
CONFIG_DIR = BASE_DIR / "config"
SECRETS_DIR = CONFIG_DIR / "secrets"
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = DATA_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"

# Configuration GitLab
GITLAB_CONFIG = {
    "DEFAULT_TIMEOUT": 30,
    "DEFAULT_MAX_RETRIES": 3,
    "DEFAULT_RETRY_DELAY": 5,
    "DEFAULT_ITEMS_PER_PAGE": 100,
    "MAX_ITEMS_PER_PAGE": 500,
    "RATE_LIMIT_DELAY": 1,
}

# Configuration de l'export
EXPORT_CONFIG = {
    "EXCEL_FORMAT": "xlsx",
    "DEFAULT_SHEET_NAME": "GitLab Users",
    "MAX_ROWS_PER_SHEET": 1000000,
    "DATE_FORMAT": "%d-%m-%Y",
    "DATETIME_FORMAT": "%d-%m-%Y %H:%M:%S",
}

# Configuration des données
DATA_QUALITY_CONFIG = {
    "MIN_QUALITY_SCORE": 80,
    "ESSENTIAL_FIELDS": ["name", "username", "email", "state"],
    "OPTIONAL_FIELDS": ["last_activity_on", "created_at", "web_url"],
    "INACTIVE_THRESHOLD_DAYS": 90,
    "LONG_INACTIVE_THRESHOLD_DAYS": 180,
}

# Configuration des logs
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_max_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5,
}

# Types de comptes reconnus
ACCOUNT_TYPES = {
    "HUMAN": "Human",
    "BOT": "Bot",
    "SERVICE": "Service",
    "GHOST": "Ghost",
}

# Indicateurs de bots
BOT_INDICATORS = [
    "bot", "service", "ci", "deploy", "automation", "system", 
    "pipeline", "runner", "webhook", "monitor", "backup"
]

# Environnements supportés
SUPPORTED_ENVIRONMENTS = ["dev", "test", "staging", "prod", "local"]

# Configuration SSL
SSL_CONFIG = {
    "VERIFY_SSL_DEFAULT": True,
    "SSL_TIMEOUT": 30,
    "SSL_CERT_VERIFY": True,
}

# Limites de sécurité
SECURITY_LIMITS = {
    "MAX_SECRET_LENGTH": 1024,
    "MAX_CONFIG_SIZE": 10 * 1024 * 1024,  # 10MB
    "MAX_EXPORT_RECORDS": 1000000,
}

# ================================
# FONCTIONS UTILITAIRES
# ================================

def get_output_path(service: str, data_type: str, timestamp: str = None) -> Path:
    """
    Génère un chemin de sortie standardisé.
    
    Args:
        service: Nom du service (gitlab, sonarqube, etc.)
        data_type: Type de données (users, projects, etc.)
        timestamp: Horodatage optionnel
        
    Returns:
        Chemin de sortie
    """
    if timestamp is None:
        from datetime import datetime
        timestamp = datetime.now().strftime("%d-%m-%Y--%H%M")
    
    output_dir = OUTPUT_DIR / service / data_type
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return output_dir / f"{service}_{data_type}_{timestamp}.{EXPORT_CONFIG['EXCEL_FORMAT']}"

def get_config_for_service(service: str) -> Dict[str, Any]:
    """
    Récupère la configuration pour un service spécifique.
    
    Args:
        service: Nom du service
        
    Returns:
        Configuration du service
    """
    configs = {
        "gitlab": GITLAB_CONFIG,
        "export": EXPORT_CONFIG,
        "data_quality": DATA_QUALITY_CONFIG,
        "logging": LOGGING_CONFIG,
        "ssl": SSL_CONFIG,
        "security": SECURITY_LIMITS,
    }
    
    return configs.get(service, {})

def validate_environment(env: str) -> bool:
    """
    Valide un environnement.
    
    Args:
        env: Nom de l'environnement
        
    Returns:
        True si l'environnement est valide
    """
    return env.lower() in SUPPORTED_ENVIRONMENTS

def get_log_config(service: str = None) -> Dict[str, Any]:
    """
    Génère la configuration de logging.
    
    Args:
        service: Nom du service (optionnel)
        
    Returns:
        Configuration de logging
    """
    config = LOGGING_CONFIG.copy()
    
    if service:
        log_file = LOGS_DIR / f"{service}.log"
        config["filename"] = str(log_file)
    
    return config

# ================================
# GESTIONNAIRE DE CONFIGURATION
# ================================


class ConfigManager:
    """Gestionnaire de configuration pour le système ETL."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise le gestionnaire de configuration.
        
        Args:
            config_path: Chemin vers le fichier de configuration. Si None, utilise le fichier dev.yaml.
        """
        self.config_path = config_path
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Charge la configuration à partir du fichier spécifié.
        
        Returns:
            Dict contenant la configuration chargée.
            
        Raises:
            FileNotFoundError: Si le fichier de configuration n'existe pas.
            ValueError: Si le fichier de configuration est invalide.
        """
        if not self.config_path:
            # Chemin par défaut: config/environments/dev.yaml
            base_path = Path(__file__).parent.parent.parent
            self.config_path = os.path.join(base_path, "config", "environments", "dev.yaml")
            
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Le fichier de configuration '{self.config_path}' n'existe pas.")
            
        try:
            with open(self.config_path, "r") as config_file:
                return yaml.safe_load(config_file)
        except yaml.YAMLError as e:
            raise ValueError(f"Erreur de parsing du fichier de configuration: {e}")
    
    def get_config(self, section: str = None) -> Dict[str, Any]:
        """
        Récupère la configuration complète ou une section spécifique.
        
        Args:
            section: Nom de la section à récupérer. Si None, retourne toute la configuration.
            
        Returns:
            Dict contenant la configuration demandée.
            
        Raises:
            KeyError: Si la section demandée n'existe pas dans la configuration.
        """
        if not section:
            return self._config
            
        if section not in self._config:
            raise KeyError(f"La section '{section}' n'existe pas dans la configuration.")
            
        return self._config[section]


# Instance singleton pour un accès global à la configuration
_config_manager = None


def get_config_manager(config_path: Optional[str] = None) -> ConfigManager:
    """
    Récupère l'instance singleton du gestionnaire de configuration.
    
    Args:
        config_path: Chemin vers le fichier de configuration à utiliser.
        
    Returns:
        Instance unique de ConfigManager.
    """
    global _config_manager
    if _config_manager is None or config_path is not None:
        _config_manager = ConfigManager(config_path)
    return _config_manager
