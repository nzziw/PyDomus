from django.contrib import admin

from .models import Device, SensorAlert, SensorReading

# Register your models here.
admin.site.register(Device)
admin.site.register(SensorReading)
admin.site.register(SensorAlert)
