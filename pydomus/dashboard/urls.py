from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("alert/", views.alert_view, name="alert"),
    path("alert/<int:pk>/delete/", views.alert_delete_view, name="alert_delete"),
    path("profil/", views.profil_view, name="profil"),
]
