from django.db import models
from django.utils import timezone


class Device(models.Model):
    class DeviceType(models.TextChoices):
        SENSOR = "sensor", "Capteur"
        SWITCH = "switch", "Interrupteur"

    topic = models.CharField(max_length=100, unique=True)
    device_type = models.CharField(max_length=20, choices=DeviceType.choices)

    def __str__(self):
        return self.topic


class SensorReading(models.Model):
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="readings"
    )
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    recorded_at = models.DateTimeField(default=timezone.now)
    battery = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.device.topic}"
