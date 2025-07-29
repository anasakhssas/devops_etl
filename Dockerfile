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

# Définir la commande par défaut
CMD ["python", "main.py"]
