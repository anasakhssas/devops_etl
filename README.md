# DevOps ETL

Plateforme d'extraction et d'analyse des données depuis les outils DevOps pour générer des KPIs de productivité et de qualité.

## À propos du projet

DevOps ETL est une solution complète d'extraction, transformation et chargement (ETL) conçue pour collecter des données à partir de différents outils DevOps, les transformer en un modèle de données cohérent et générer des KPIs pertinents pour mesurer la productivité des développeurs et la qualité des projets.

### Sources de données supportées

- **GitLab** : Commits, merge requests, issues, pipelines
- **SonarQube** : Métriques de qualité de code, code smells, vulnérabilités
- **DefectDojo** : Rapports de sécurité, vulnérabilités, conformité
- **Dependency Track** : Analyse des dépendances, vulnérabilités des composants

### Principales fonctionnalités

- Extraction incrémentielle des données depuis les APIs
- Transformation en modèle dimensionnel
- Historisation des changements (SCD Type 2)
- Corrélation entre les différentes sources
- Calcul automatisé de KPIs de productivité et qualité
- Export des données vers Excel (Phase 1) et PostgreSQL (Phase 2)
- Dashboarding via Power BI

## Architecture

Cette solution ETL suit les principes de l'Architecture Hexagonale (Ports et Adaptateurs) pour assurer une séparation claire entre :
- Les **adaptateurs d'entrée** (sources de données des outils DevOps)
- Le **domaine** métier (entités, modèles et transformations)
- Les **adaptateurs de sortie** (stockage Excel, PostgreSQL, Power BI)

Pour plus de détails sur l'architecture, consultez [Architecture détaillée](docs/02_ARCHITECTURE.md).

## Structure du projet

```
devops_etl/
├── src/                         # Code source
│   ├── core/                    # Fonctionnalités transversales
│   ├── domain/                  # Modèle de domaine
│   ├── extractors/              # Extraction depuis les sources
│   ├── transformers/            # Transformation des données
│   ├── loaders/                 # Chargement des données
│   ├── validators/              # Validation des données
│   ├── models/                  # Modèles analytiques
│   ├── analytics/               # Analyse et KPIs
│   ├── orchestration/           # Orchestration des pipelines
│   ├── shared/                  # Éléments partagés
│   ├── containers.py            # Injection de dépendances
│   └── main.py                  # Point d'entrée
├── tests/                       # Tests unitaires et d'intégration
├── config/                      # Configuration
├── data/                        # Données (cache, output)
├── docs/                        # Documentation
└── reports/                     # Rapports générés
```

## Prérequis

- Python 3.10+
- Docker et Docker Compose (pour le déploiement)
- Accès aux APIs des outils DevOps
  - GitLab
  - SonarQube
  - DefectDojo
  - Dependency Track

## Installation

### Installation locale pour le développement

```bash
# Cloner le repository
git clone <repo-url>
cd devops-etl

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sous Windows

# Installer les dépendances
pip install -e .
pip install -r requirements-dev.txt  # Pour les dépendances de développement
```

### Configuration

Créez un fichier `.env` à partir du modèle :

```bash
cp config/environments/dev.yaml config/environments/.env.yaml
```

Éditez le fichier pour configurer les accès aux APIs :

```yaml
gitlab:
  api_url: https://gitlab.example.com/api/v4
  private_token: your_private_token

sonarqube:
  api_url: https://sonarqube.example.com/api
  auth_token: your_auth_token

# ... autres configurations
```

## Utilisation

### Exécution complète de l'ETL

```bash
# Exécution avec les paramètres par défaut
python -m src.main

# Exécution avec des paramètres spécifiques
python -m src.main --config config/environments/prod.yaml --date-from 2023-01-01
```

### Extraction depuis une source spécifique

```bash
python -m src.main --source gitlab
```

### Options disponibles

- `--config` : Chemin vers le fichier de configuration
- `--source` : Source(s) à extraire (gitlab, sonarqube, defect_dojo, dependency_track)
- `--date-from` : Date de début pour l'extraction incrémentielle
- `--date-to` : Date de fin pour l'extraction
- `--full` : Mode d'extraction complète (non incrémentielle)
- `--dry-run` : Simulation sans écriture

## Déploiement avec Docker

```bash
# Construire l'image
docker build -t devops-etl .

# Exécuter le conteneur (avec persistance des données)
docker run --env-file .env -v ./data:/app/data devops-etl
```

### Configuration du fichier .env

Créez un fichier `.env` à la racine du projet pour vos variables d'environnement (exemple : jetons d'API, URLs, etc.).  
Ce fichier sera chargé automatiquement par le conteneur.

### Utilisation des volumes

Le montage du volume `-v ./data:/app/data` permet de conserver les fichiers extraits et les rapports générés en dehors du conteneur.

### Docker Compose

Un exemple de fichier `docker-compose.yml` :

```yaml
version: "3.8"
services:
  devops-etl:
    build: .
    container_name: devops-etl
    env_file:
      - .env
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

Lancez le projet avec :

```bash
docker-compose up --build
```

### Développement avec Docker

Pour lancer un shell interactif dans le conteneur :

```bash
docker run -it --env-file .env -v ./data:/app/data devops-etl /bin/bash
```

## Docker

Pour builder et lancer le projet dans un conteneur Docker :

```bash
docker build -t devops-etl .
docker run --env-file .env devops-etl
```

Pour utiliser docker-compose (si besoin) :

```bash
docker-compose up --build
```

## KPIs disponibles

### Productivité

- Vélocité par développeur/équipe
- Temps moyen de cycle (de l'ouverture d'une issue à sa livraison)
- Temps moyen de review des MRs
- Fréquence des déploiements

### Qualité

- Dette technique
- Couverture de code
- Densité de bugs
- Nombre de vulnérabilités (par sévérité)
- Respect des standards de code

## Documentation

La documentation complète est disponible dans le répertoire `docs/` :

- [Guide d'onboarding](docs/01_ONBOARDING.md)
- [Architecture détaillée](docs/02_ARCHITECTURE.md)
- [Modèle de données](docs/03_DATA_MODEL.md)
- [ADRs (Architecture Decision Records)](docs/04_ADR/)

## Contribution

1. Forker le projet
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Committer vos changements (`git commit -m 'Add some amazing feature'`)
4. Pousser vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Merge Request

## Licence

Ce projet est sous licence [LICENSE] - voir le fichier LICENSE.md pour plus de détails.

## Équipe

- [Nom Prénom] - Rôle - Email
