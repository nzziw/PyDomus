from django.shortcuts import render
from django_otp.decorators import otp_required
from .models import Device, SensorReading, ServiceStatus, SensorAlert

# Create your views here.
@otp_required
def home_view(request):
    sensors = []
    for device in Device.objects.filter(device_type=Device.DeviceType.SENSOR):
        sensors.append({"device": device, "last_reading": device.readings.first()})
    return render(request, "dashboard/index.html", {"sensors": sensors})