
# Image de base : Python 3.13
FROM python:3.13

# Définit le dossier de travail dans le conteneur
WORKDIR /app/pydomus

# Copie le fichier des dépendances dans le conteneur
COPY requirements.txt .

# Installe toutes les bibliothèques nécessaires au projet Django
RUN pip install --no-cache-dir -r requirements.txt

# Copie le code de l'application Django dans le conteneur
COPY pydomus/ .

# Indique que l'application utilise le port 8000
EXPOSE 8000

# Commande exécutée au démarrage du conteneur
# Lance l'application Django avec Gunicorn
CMD ["gunicorn", "pydomus.wsgi:application", "--bind", "0.0.0.0:8000"]