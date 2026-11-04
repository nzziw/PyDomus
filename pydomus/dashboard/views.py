from django.shortcuts import render
from django_otp.decorators import otp_required
from .models import Device, SensorReading, ServiceStatus, SensorAlert
from account.models import Account

# Create your views here.
@otp_required
def home_view(request):
    sensors = []
    for device in Device.objects.filter(device_type=Device.DeviceType.SENSOR):
        sensors.append({"device": device, "last_reading": device.readings.first()})
    return render(request, "dashboard/index.html", {"sensors": sensors})

@otp_required
def alert_view(request):
    alerts_temperature = request.user.alerts.filter(metric="temperature")
    alerts_humidity = request.user.alerts.filter(metric="humidity")
    return render(request, "dashboard/alerts.html", {"alerts_temperature": alerts_temperature, "alerts_humidity": alerts_humidity})