# Utilise une image Python officielle
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Variable d'environnement pour éviter le buffering
ENV PYTHONUNBUFFERED=1

# Initialiser la base de données Airflow au démarrage et lancer le webserver
CMD ["sh", "-c", "airflow db init && airflow webserver --port 8080"]
