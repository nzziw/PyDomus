
FROM python:3.13

WORKDIR /app

# Installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code Django
COPY pydomus/ ./pydomus/

# Port utilisé par Django
EXPOSE 8000

# Démarrage de l'application
CMD ["python", "pydomus/manage.py", "runserver", "0.0.0.0:8000"]
