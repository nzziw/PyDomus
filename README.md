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

### 1. Cloner le dépôt
```bash
git clone https://github.com/Unclad5572/PyDomus.git
cd PyDomus
```

## 2. Créer l'environnement virtuel et installer les dépendances
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configurer les variables d'environnement
```bash
cp .env.example .env
```
Modifiez ce que vous souhaitez dans le .env

### 4. Créer l'environnement virtuel et installer les dépendances
```bash
docker compose up -d
```

### 5. Appliquer les migrations et lancer le serveur
```bash
python3 pydomus/manage.py migrate
python3 pydomus/manage.py runserver 0.0.0.0:8000
```