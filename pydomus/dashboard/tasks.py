import requests
from django.conf import settings


def call(methode, timeout_http=10, **params):
    # Call the Telegram Bot API with the specified method and parameters
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/{methode}"
    reponse = requests.post(url, json=params, timeout=timeout_http)
    reponse.raise_for_status()
    return reponse.json()["result"]


def send_message(chat_id, texte):
    return call("sendMessage", chat_id=chat_id, text=texte)
