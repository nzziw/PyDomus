from account.models import TelegramAccount
from django.conf import settings
from django.shortcuts import redirect, render
from django_otp.decorators import otp_required

from .forms import SensorAlertForm
from .models import Device


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
            data = form.cleaned_data
            if request.user.alerts.filter(**data).exists():
                form.add_error(None, "Cette alerte existe déjà.")
            else:
                request.user.alerts.update_or_create(
                    device=data["device"],
                    metric=data["metric"],
                    operator=data["operator"],
                    defaults={"threshold": data["threshold"]},
                )
                return redirect("dashboard:alert")
    else:
        form = SensorAlertForm()

    return render(
        request,
        "dashboard/alerts.html",
        {
            "form": form,
            "alerts_temperature": request.user.alerts.filter(metric="temperature"),
            "alerts_humidity": request.user.alerts.filter(metric="humidity"),
        },
    )


@otp_required
def alert_delete_view(request, pk):
    if request.method == "POST":
        alert = request.user.alerts.filter(pk=pk).first()
        if alert:
            alert.delete()
    return redirect("dashboard:alert")


@otp_required
def profil_view(request):
    compte, created = TelegramAccount.objects.get_or_create(user=request.user)
    lien = f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start={compte.link_code}"
    return render(request, "dashboard/profil.html", {"compte": compte, "lien": lien})
