import json

import paho.mqtt.client as mqtt
from dashboard.models import Device, SensorAlert, SensorReading, ServiceStatus
from dashboard.tasks import notify
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone


# Functions to manage the service status in the database
def set_status(name, online):
    ServiceStatus.objects.update_or_create(name=name, defaults={"online": online})


def check_alerts(reading):
    alerts = SensorAlert.objects.filter(device=reading.device)

    for alert in alerts:
        if alert.metric == "temperature":
            value = reading.temperature  # If the alert is for temperature, get the temperature value from the reading
        else:
            value = (
                reading.humidity
            )  # If the alert is for humidity, get the humidity value from the reading

        if value is None:
            continue

        exceeded = alert.is_exceeded(value)

        if (
            exceeded and not alert.triggered
        ):  # If the alert is exceeded and not already triggered, trigger it
            alert.triggered = True
            alert.triggered_at = timezone.now()
            alert.save()
            notify(  # Send a notification to the user via Telegram
                alert.user,
                f"Alerte déclenchée pour le capteur {alert.device.name} : "
                f"{alert.get_metric_display()} {value} {alert.unit} "
                f"({alert.get_operator_display()} {alert.threshold} {alert.unit})",
            )
            print(f"Alerte déclenchée : {alert}")
        elif (
            not exceeded and alert.triggered
        ):  # If the alert is no longer exceeded and was previously triggered, reset it
            alert.triggered = False
            alert.triggered_at = None
            alert.save()
            print(f"Alerte terminée : {alert}")


# MQTT callbacks


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Échec de connexion : {reason_code}")
        set_status("broker", False)
    else:
        print("Connecté à Mosquitto avec succès")
        set_status("broker", True)
        client.subscribe(
            [
                (f"{settings.BROKER_TOPIC}/+", 0),  # measurements from all devices
                (
                    f"{settings.BROKER_TOPIC}/bridge/state",
                    0,
                ),  # Zigbee2MQTT online / offline
            ]
        )


def on_disconnect(client, userdata, flags, reason_code, properties):
    print(f"Déconnecté : {reason_code}")
    set_status("broker", False)


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    print(f"Abonnement : {reason_code_list}")


def on_message(client, userdata, msg):
    print(f"[{msg.topic}] {msg.payload.decode(errors='replace')}")
    if msg.topic == f"{settings.BROKER_TOPIC}/bridge/state":
        texte = msg.payload.decode(errors="replace")
        try:
            etat = json.loads(texte).get(
                "state"
            )  # latest version : {"state": "online"}
        except (json.JSONDecodeError, AttributeError):
            etat = texte  # legacy version : "online" or "offline"
        set_status(
            "zigbee2mqtt", etat == "online"
        )  # Update the status of Zigbee2MQTT in the database
        print(f"Zigbee2MQTT : {etat}")
        return

    try:
        data = json.loads(
            msg.payload.decode()
        )  # Convert the JSON message into a Python dict
    except (UnicodeDecodeError, json.JSONDecodeError):
        print(f"Message illisible ignoré : {msg.topic}")
        return

    device, created = (
        Device.objects.get_or_create(  # Create a new device if it doesn't exist
            topic=msg.topic,
            defaults={"device_type": Device.DeviceType.SENSOR},
        )
    )
    if created:  # If a new device was created, print a message
        print(f"Nouvel appareil créé : {device}")

    reading = (
        SensorReading.objects.create(  # Create a new sensor reading for the device
            device=device,
            temperature=data.get("temperature"),
            humidity=data.get("humidity"),
            battery=data.get("battery"),
        )
    )
    print(f"Nouvelle lecture enregistrée pour {device}: {data}")
    # Check if any alerts are triggered by this new reading
    check_alerts(reading)


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
