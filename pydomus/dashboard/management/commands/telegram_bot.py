import time

import requests
from account.models import TelegramAccount
from dashboard.tasks import call, send_message
from django.core.management.base import BaseCommand
from django.db import close_old_connections
from django.utils import timezone


def handle_incoming_message(chat_id, texte):
    if not texte.startswith("/start"):
        send_message(
            chat_id,
            "Je sers uniquement à envoyer des alertes PyDomus. Tu ne peux pas m'envoyer de messages. Merci !",
        )
        return

    morceaux = texte.split(
        maxsplit=1
    )  # Verify if the user has provided a token after /start
    if len(morceaux) < 2:
        send_message(
            chat_id,
            "Pour lier votre compte, utilisez le lien depuis votre profil PyDomus.",
        )
        return

    code = morceaux[1]
    try:
        compte = TelegramAccount.objects.get(link_code=code)
    except TelegramAccount.DoesNotExist:
        send_message(chat_id, "Lien invalide.")
        return

    compte.chat_id = chat_id
    compte.linked_at = timezone.now()
    compte.save()

    send_message(
        chat_id,
        f"Bienvenue sur votre Bot Telegram {compte.user.username} ! Vous recevrez ici vos alertes personnalisées que vous pouvez configurer depuis votre Dashboard.",
    )
    print(f"Telegram lié : {compte.user} chatid : {chat_id}")


class Command(BaseCommand):
    help = "Listen for incoming messages from the Telegram bot and handle them."

    def handle(self, *args, **options):
        print("Bot Telegram démarré, en attente de messages...")
        offset = None

        while True:
            try:
                updates = call(
                    "getUpdates",
                    timeout_http=40,
                    timeout=30,
                    offset=offset,
                    allowed_updates=["message"],
                )
            except requests.RequestException as e:
                print(f"Erreur réseau : {e}. Nouvel essai dans 5 s")
                time.sleep(5)
                continue

            close_old_connections()

            for update in updates:
                offset = update["update_id"] + 1

                message = update.get("message")
                if message is None:
                    continue

                chat_id = message["chat"]["id"]
                texte = message.get("text", "")
                print(f"Message reçu de {chat_id} : {texte}")

                try:
                    handle_incoming_message(chat_id, texte)
                except Exception as e:
                    print(f"Erreur en traitant le message : {e}")
