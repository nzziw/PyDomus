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

    def clean_threshold(self):
        threshold = self.cleaned_data["threshold"]
        if self.cleaned_data.get("metric") == "battery" and not 0 <= threshold <= 100:
            self.add_error(None, "Le seuil de batterie doit être entre 0 et 100 %.")
        return threshold
