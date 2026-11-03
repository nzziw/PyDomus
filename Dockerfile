
# Image de base : Python 3.13
FROM python:3.13

# Définit le dossier de travail dans le conteneur
WORKDIR /app

# Copie le fichier des dépendances dans le conteneur
COPY requirements.txt .

# Installe toutes les bibliothèques nécessaires au projet Django
RUN pip install --no-cache-dir -r requirements.txt

# Copie le code de l'application Django dans le conteneur
COPY pydomus/ ./pydomus/

# Indique que l'application utilise le port 8000
EXPOSE 8000

# Commande exécutée au démarrage du conteneur
# Lance le serveur Django et le rend accessible depuis l'extérieur
CMD ["python", "pydomus/manage.py", "runserver", "0.0.0.0:8000"]
