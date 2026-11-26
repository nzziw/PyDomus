import os

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_default_admin(apps, schema_editor):
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(app_label, model_name)

    username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")

    if not username or not password:
        return  # Not creating superuser if username or password is not provided

    User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "password": make_password(password),  # hash the password before saving
            "is_staff": True,
            "is_superuser": True,
            "is_active": True,
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0005_telegramaccount"),
    ]

    operations = [
        migrations.RunPython(create_default_admin, migrations.RunPython.noop),
    ]
