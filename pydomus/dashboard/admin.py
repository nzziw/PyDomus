from django.contrib import admin

from .models import Device, SensorReading

# Register your models here.
admin.site.register(Device)
admin.site.register(SensorReading)
