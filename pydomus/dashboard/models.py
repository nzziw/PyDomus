from django.conf import settings
from django.db import models
from django.utils import timezone


class Device(models.Model):
    class DeviceType(models.TextChoices):
        SENSOR = "sensor", "Capteur"
        SWITCH = "switch", "Interrupteur"

    topic = models.CharField(max_length=100, unique=True)
    device_type = models.CharField(max_length=20, choices=DeviceType.choices)

    @property
    def name(self):
        return self.topic.split("/")[-1]  # "home/salon" to "salon"

    def __str__(self):
        return self.name


class ServiceStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Name of the service
    online = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Service Statuses"

    def __str__(self):
        return f"{self.name} : {'UP' if self.online else 'DOWN'}"


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


class SensorAlert(models.Model):
    class Metric(models.TextChoices):
        TEMPERATURE = "temperature", "Température"
        HUMIDITY = "humidity", "Humidité"
        BATTERY = "battery", "Batterie"

    class Operator(models.TextChoices):
        GREATER = "gt", "supérieure à"
        LESS = "lt", "inférieure à"

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="alerts",
        limit_choices_to={"device_type": Device.DeviceType.SENSOR},
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="alerts",
    )
    metric = models.CharField(max_length=20, choices=Metric.choices)
    operator = models.CharField(max_length=2, choices=Operator.choices)
    threshold = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)

    triggered = models.BooleanField(default=False)
    triggered_at = models.DateTimeField(null=True, blank=True)

    def is_exceeded(self, value):
        # Returns True if the value exceeds the threshold based on the operator, False otherwise.
        if value is None:
            return False
        if self.operator == self.Operator.GREATER:
            return value > self.threshold
        return value < self.threshold

    @property
    def current_value(self):
        # Returns the latest reading for the specified metric of the associated device, or None if no readings are available.
        reading = self.device.readings.first()
        if reading is None:
            return None
        return getattr(reading, self.metric)

    @property
    def unit(self):
        return "°C" if self.metric == self.Metric.TEMPERATURE else "%"

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.device.topic} : {self.get_metric_display()} "
            f"{self.get_operator_display()} {self.threshold}"
        )
