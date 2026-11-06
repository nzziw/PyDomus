# Base image: Python 3.13
FROM python:3.13-slim

# Prevent Python from writing .pyc files and disable output buffering so stdout/stderr show up in podman logs
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

# Set the working directory inside the container
WORKDIR /app/pydomus

# Copy the dependency file into the container
COPY requirements.txt .

# Install all the libraries required by the Django project
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django application code into the container
COPY pydomus/ .

# Document that the application listens on port 8000
EXPOSE 8000

# Command run when the container starts
# Starts the Django application with Gunicorn
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]