from django.urls import path

from . import views

app_name = "account"

urlpatterns = [
    path("", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("mfa-setup/", views.mfa_setup, name="mfa-setup"),
    path("mfa-verify/", views.mfa_verify, name="mfa-verify"),
    path("mfa-backup-codes/", views.mfa_backup_codes, name="mfa-backup-codes"),
]
