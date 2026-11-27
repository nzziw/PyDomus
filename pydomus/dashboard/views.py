from datetime import timedelta

import plotly.graph_objects as go
from account.models import TelegramAccount
from django.conf import settings
from django.shortcuts import redirect, render
from django.utils import timezone
from django_otp.decorators import otp_required

from .forms import SensorAlertForm
from .models import Device, SensorReading

# Constants authorized for the graph view
PERIODS = {1: "1 heure", 24: "24 heures", 168: "7 jours", 720: "30 jours"}
PERIOD_DEFAUT = 24

# Choices the metric for the graph view
METRICS = {"temperature": "Température", "humidity": "Humidité"}
UNITS = {"temperature": "°C", "humidity": "%"}
METRIC_DEFAUT = "temperature"

# Chart colors
CHART_ACCENT = "#2f80ed"
CHART_MUTED = "#8a96a3"
CHART_GRID = "rgba(138, 150, 163, 0.18)"
CHART_FONT = (
    '"Segoe UI", system-ui, -apple-system, Roboto, Helvetica, Arial, sans-serif'
)


# Create your views here.
#home_view get data of all type of devices 
@otp_required
def home_view(request):
    devices = []
    for device in Device.objects.all():
        if device.device_type == Device.DeviceType.SWITCH:
            last_reading = device.switch_readings.first()
        else:
            last_reading = device.readings.first()
        devices.append({"device": device, "last_reading": last_reading})
    triggered_alerts = request.user.alerts.filter(triggered=True)

    return render(
        request,
        "dashboard/index.html",
        {"devices": devices, "triggered_alerts": triggered_alerts},
    
    )


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
            "alerts_battery": request.user.alerts.filter(metric="battery"),
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


@otp_required
def chart_view(request):
    # Only sensors
    devices = Device.objects.filter(device_type=Device.DeviceType.SENSOR).order_by(
        "topic"
    )

    # Selected sensor (first one by default)
    device = None
    device_id = request.GET.get("device", "")
    if device_id.isdigit():
        device = devices.filter(pk=int(device_id)).first()
    if device is None:
        device = devices.first()

    # Selected period (24 h by default)
    try:
        period = int(request.GET.get("period", PERIOD_DEFAUT))
    except ValueError:
        period = PERIOD_DEFAUT
    if period not in PERIODS:
        period = PERIOD_DEFAUT

    metric = request.GET.get("metric", METRIC_DEFAUT)
    if metric not in METRICS:
        metric = METRIC_DEFAUT
    unit = UNITS[metric]

    chart_html = None
    if device is not None:
        since = timezone.now() - timedelta(hours=period)
        measurements = list(
            SensorReading.objects.filter(
                device=device,
                recorded_at__gte=since,
                temperature__isnull=False,
            )
            .order_by("recorded_at")
            .values_list("recorded_at", metric)
        )

        if measurements:
            x = [timezone.localtime(ts).replace(tzinfo=None) for ts, _ in measurements]
            y = [value for _, value in measurements]

            # Start and end of the X axis = the selected period
            start = timezone.localtime(since).replace(tzinfo=None)
            end = timezone.localtime(timezone.now()).replace(tzinfo=None)

            # The curve
            fig = go.Figure(
                go.Scatter(
                    x=x,
                    y=y,
                    mode="lines+markers",
                    marker=dict(size=5),
                    line=dict(color="#2f80ed", width=2.5),  # same blue as the site
                    hovertemplate="%{y:.1f} "
                    + unit
                    + "<br>%{x|%d/%m %H:%M}<extra></extra>",
                )
            )

            # The look of the chart
            fig.update_layout(
                height=380,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",  # transparent background
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(
                    color="#8a96a3"
                ),  # grey text, readable in light and dark mode
                xaxis=dict(
                    showgrid=False,
                    tickformat="%H:%M<br>%d/%m",
                    range=[start, end],
                ),
                yaxis=dict(gridcolor="rgba(138, 150, 163, 0.2)", ticksuffix=" " + unit),
            )

            chart_html = fig.to_html(
                full_html=False,
                include_plotlyjs=False,
                config={"displayModeBar": False},  # hide the toolbar
            )

        measurements = [(ts, value) for ts, value in measurements if value is not None]

    return render(
        request,
        "dashboard/chart.html",
        {
            "devices": devices,
            "device": device,
            "periods": PERIODS.items(),
            "period": period,
            "chart": chart_html,
            "metrics": METRICS.items(),
            "metric": metric,
        },
    )
