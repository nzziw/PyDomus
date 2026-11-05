from django import forms
from .models import SensorAlert


class SensorAlertForm(forms.ModelForm):
    class Meta:
        model = SensorAlert
        fields = ["device", "metric", "operator", "threshold"]
        labels = {
            "device": "Capteur",
            "metric": "Mesure",
            "operator": "Condition",
            "threshold": "Seuil",
        }
