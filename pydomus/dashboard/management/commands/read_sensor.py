import json

import paho.mqtt.client as mqtt
from dashboard.models import Device, SensorReading
from django.conf import settings
from django.core.management.base import BaseCommand


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Échec de connexion : {reason_code}")
    else:
        print("Connecté à Mosquitto avec succès")
        client.subscribe(f"{settings.BROKER_TOPIC}/+")


def on_disconnect(client, userdata, flags, reason_code, properties):
    print(f"Déconnecté : {reason_code}")


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    print(f"Abonnement : {reason_code_list}")


def on_message(client, userdata, msg):
    print(f"[{msg.topic}] {msg.payload.decode(errors='replace')}")

    try:
        data = json.loads(
            msg.payload.decode()
        )  # Convert the JSON message into a Python dict
    except (UnicodeDecodeError, json.JSONDecodeError):
        print(f"Message illisible ignoré : {msg.topic}")
        return 1

    device, created = (
        Device.objects.get_or_create(  # Create a new device if it doesn't exist
            topic=msg.topic,
            defaults={"device_type": Device.DeviceType.SENSOR},
        )
    )
    if created:  # If a new device was created, print a message
        print(f"Nouvel appareil créé : {device}")

    SensorReading.objects.create(  # Create a new sensor reading for the device
        device=device,
        temperature=data.get("temperature"),
        humidity=data.get("humidity"),
        battery=data.get("battery"),
    )
    print(f"Nouvelle lecture enregistrée pour {device}: {data}")


class Command(BaseCommand):
    help = "Écoute le broker MQTT et affiche les messages reçus"

    def handle(self, *args, **options):
        client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        client.enable_logger()
        client.username_pw_set(settings.BROKER_USERNAME, settings.BROKER_PASSWORD)
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_subscribe = on_subscribe
        client.on_message = on_message

        client.connect(settings.BROKER_BROKER, settings.BROKER_PORT, keepalive=60)
        client.loop_forever()
