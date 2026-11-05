import secrets

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


def nouveau_code():
    return secrets.token_hex(16)  # 32 random hexadecimal characters


# Create your models here.
class Account(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


class TelegramAccount(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="telegram"
    )
    link_code = models.CharField(max_length=32, unique=True, default=nouveau_code)
    chat_id = models.BigIntegerField(null=True, blank=True)
    linked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} : {'lié' if self.chat_id else 'non lié'}"
