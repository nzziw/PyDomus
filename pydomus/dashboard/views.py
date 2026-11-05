from django.shortcuts import render, redirect
from django_otp.decorators import otp_required
from .models import Device, SensorReading, ServiceStatus, SensorAlert
from account.models import Account
from .forms import SensorAlertForm

# Create your views here.
@otp_required
def home_view(request):
    sensors = []
    for device in Device.objects.filter(device_type=Device.DeviceType.SENSOR):
        sensors.append({"device": device, "last_reading": device.readings.first()})
    return render(request, "dashboard/index.html", {"sensors": sensors})

@otp_required
def alert_view(request):
    if request.method == "POST":
        form = SensorAlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.user = request.user
            alert.save()
            return redirect("dashboard:alert")
    else:
        form = SensorAlertForm()

    return render(request, "dashboard/alerts.html", {
        "form": form,
        "alerts_temperature": request.user.alerts.filter(metric="temperature"),
        "alerts_humidity": request.user.alerts.filter(metric="humidity"),
    })