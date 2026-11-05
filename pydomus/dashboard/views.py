<<<<<<< HEAD
from django.shortcuts import render, redirect
from django_otp.decorators import otp_required
from .models import Device, SensorReading, ServiceStatus, SensorAlert
from account.models import Account
from .forms import SensorAlertForm
=======
from account.models import TelegramAccount
from django.conf import settings
from django.shortcuts import render
from django_otp.decorators import otp_required

from .models import Device

>>>>>>> c7657b6 (add: create profile view and template for telegram account linking)

# Create your views here.
@otp_required
def home_view(request):
    sensors = []
    for device in Device.objects.filter(device_type=Device.DeviceType.SENSOR):
        sensors.append({"device": device, "last_reading": device.readings.first()})
    return render(request, "dashboard/index.html", {"sensors": sensors})

<<<<<<< HEAD
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

@otp_required
def alert_delete_view(request, pk):
    if request.method == "POST":
        alert = request.user.alerts.filter(pk=pk).first()
        if alert:
            alert.delete()
    return redirect("dashboard:alert")
=======

@otp_required
def profil_view(request):
    compte, created = TelegramAccount.objects.get_or_create(user=request.user)
    lien = f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start={compte.link_code}"
    return render(request, "dashboard/profil.html", {"compte": compte, "lien": lien})
>>>>>>> c7657b6 (add: create profile view and template for telegram account linking)
