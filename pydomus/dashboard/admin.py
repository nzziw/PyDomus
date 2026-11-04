from django.contrib import admin

from .models import Device, SensorAlert, SensorReading, ServiceStatus

# Register your models here.
admin.site.register(Device)
admin.site.register(SensorReading)
admin.site.register(SensorAlert)
admin.site.register(ServiceStatus)
