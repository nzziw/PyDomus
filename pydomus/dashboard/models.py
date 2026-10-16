from django.db import models

# Create your models here.


class TemperatureSensor(models.Model):
    topic = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        "account.Account", on_delete=models.CASCADE, related_name="sensors"
    )

    def __str__(self):
        return f"{self.topic} / {self.name}"
