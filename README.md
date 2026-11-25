# PyDomus
# Plateforme de supervision domotique — Projet INFO PRO 8501

Application web (basée sur python) de domotique permettant de superviser et piloter un domicile depuis une interface centralisée, à partir de capteurs et d'actionneurs **Zigbee**.

## Présentation

La plateforme permet à l'utilisateur de :

- visualiser **en temps réel** les mesures remontées par ses capteurs ;
- consulter l'**historique** des mesures ;
- être **alerté** en cas d'anomalie (dépassement de seuil ou capteur silencieux) ;
- **commander un actionneur** (prise électrique connectée) depuis l'interface.

Les grandeurs supervisées sont la **température**, le **taux d'humidité** et l'**ouverture des portes**.

## Fonctionnalités

| ID    | Fonction                                                                  |
|-------|---------------------------------------------------------------------------|
| BF-01 | Le système doit collecter les mesures de N capteurs (température, humidité, ouverture) |
| BF-02 | Le système doit afficher l'état courant et l'historique sur une interface graphique rafraîchie en temps réel |
| BF-03 | Le système doit lever une alerte visuelle en cas de dépassement de seuil ou de silence d'un capteur |
| BF-04 | Le système doit permettre d'envoyer des notifications via Telegram à l'utilisateur |
| BF-05 | Le système doit permettre à l'utilisateur de commander un actionneur depuis l'interface (prise électrique dans notre cas) |
| BF-06 | Le système doit communiquer en réseau avec les capteurs et actionneurs |

**Hors périmètre :** application mobile, capteurs non compatibles Zigbee.

## Contraintes techniques
* Python 3.13+
* Communication capteurs via Zigbee2MQTT
* Interface web, accessible sans installation côté client
* Mise à jour des données en temps réel (quelques secondes maximum entre la mesure et l'affichage)
* Configuration de seuils d'alertes personnalisable par l'utilisateur
* Envoi de notifications via un Bot Telegram pour avertir l'utilisateur si un seuil d'alerte est ateint.

## Matériel
* 2 capteurs Zigbee (température / humidité, ouverture de porte)
* 1 prise électrique Zigbee
* 1 adaptateur (dongle) Zigbee compatible Zigbee2MQTT
* 1 VM (avec containers Zigbee2MQTT and MQTT)

## Installation depuis les sources

### Prérequis
* Git
* Podman et `podman compose` (ou Docker et `docker compose`)
* Un broker MQTT et Zigbee2MQTT déjà opérationnels et joignables depuis la machine
* Un bot Telegram (token et nom d'utilisateur fournis par [@BotFather](https://t.me/BotFather))

### 1. Cloner le dépôt
```bash
git clone https://github.com/nzziw/PyDomus.git
cd PyDomus
```

### 2. Configurer les variables d'environnement
```bash
cp .env.example .env
```
Renseignez ensuite le fichier `.env` :

| Variable | Description |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Clé secrète Django, à générer avec `python3 -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DJANGO_DEBUG` | `True` uniquement en développement, `False` sinon |
| `DJANGO_ALLOWED_HOSTS` | IP et/ou noms de domaine utilisés pour accéder à l'application, séparés par des virgules |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Identifiants de la base PostgreSQL (créée automatiquement au premier démarrage) |
| `POSTGRES_HOST`, `POSTGRES_PORT` | Laisser `db` et `5432` (nom du service dans `docker-compose.yml`) |
| `BROKER_IP`, `BROKER_PORT` | Adresse et port du broker MQTT |
| `BROKER_USERNAME`, `BROKER_PASSWORD` | Identifiants du broker MQTT |
| `BROKER_TOPIC` | Topic de base de Zigbee2MQTT (ex. `home`, les équipements publiant sur `home/<equipement>`) |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_BOT_USERNAME` | Token et nom d'utilisateur du bot Telegram |

### 3. Lancer la stack
```bash
podman compose up -d
```
L'image `ghcr.io/nzziw/pydomus:latest` est téléchargée automatiquement au premier lancement. Cette commande démarre les services suivants :

| Service | Rôle |
|---------|------|
| `db` | Base de données PostgreSQL 16 |
| `django` | Application web (Gunicorn) ; les migrations et `collectstatic` sont exécutés automatiquement au démarrage |
| `read_sensor` | Abonnement MQTT : lecture des capteurs et pilotage de la prise |
| `telegram_bot` | Bot Telegram d'envoi des notifications |
| `caddy` | Reverse proxy et service des fichiers statiques |

Vérifiez que tous les conteneurs sont démarrés :
```bash
podman compose ps
```

### 4. Créer un compte administrateur
```bash
podman compose exec django python manage.py createsuperuser
```

### 5. Accéder à l'application
L'interface est disponible sur `http://<ip-ou-domaine>:8080`.

### Mise à jour
```bash
podman compose pull
podman compose up -d
```

### Consulter les logs
```bash
podman compose logs -f django read_sensor telegram_bot
```
