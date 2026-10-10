from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class Account(AbstractUser):
    email = models.EmailField(unique=True)
    totp_secret = models.CharField(max_length=32, blank=True)

    def __str__(self):
        return self.username
