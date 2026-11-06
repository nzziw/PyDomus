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


def notify(user, text):
    account = getattr(user, "telegram", None)  # user.telegram or None
    if (
        account is None or account.chat_id is None
    ):  # if the user has no linked Telegram account, do nothing
        return
    try:
        send_message(
            account.chat_id, text
        )  # send the message to the user's Telegram account
    except Exception as e:
        print(f"Échec de l'envoi Telegram à {user} : {e}")
