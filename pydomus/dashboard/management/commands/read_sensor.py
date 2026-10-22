import logging
import os
from pathlib import Path

import paho.mqtt.client as mqtt
from django.core.management.base import BaseCommand
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

logging.basicConfig(level=logging.DEBUG)

BROKER = os.environ["BROKER_IP"]
PORT = int(os.environ["BROKER_PORT"])
USERNAME = os.environ["BROKER_USERNAME"]
PASSWORD = os.environ["BROKER_PASSWORD"]


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Échec de connexion : {reason_code}")
    else:
        print("Connecté à Mosquitto avec succès")
        client.subscribe(os.environ["MQTT_TOPIC"])


def on_disconnect(client, userdata, flags, reason_code, properties):
    print(f"Déconnecté : {reason_code}")


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    print(f"Abonnement : {reason_code_list}")


def on_message(client, userdata, msg):
    print(f"[{msg.topic}] {msg.payload.decode(errors='replace')}")


class Command(BaseCommand):
    help = "Écoute le broker MQTT et affiche les messages reçus"

    def handle(self, *args, **options):
        client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        client.enable_logger()
        client.username_pw_set(USERNAME, PASSWORD)
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_subscribe = on_subscribe
        client.on_message = on_message

        client.connect(BROKER, PORT, keepalive=60)
        client.loop_forever()
