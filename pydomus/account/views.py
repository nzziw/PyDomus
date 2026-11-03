import base64
import io

import django_otp
import qrcode
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django_otp import match_token, user_has_device
from django_otp.decorators import otp_required
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            password1 = form.cleaned_data["password1"]
            if password1 != form.cleaned_data["password2"]:
                form.add_error("password2", "Les mots de passe ne correspondent pas.")
            else:
                Account.objects.create_user(
                    username=form.cleaned_data["username"],
                    email=form.cleaned_data["email"],
                    password=password1,
                )
                messages.success(
                    request, "Inscription réussie. Veuillez vous connecter."
                )
                return redirect("account:login")
    else:
        form = RegisterForm()
    return render(request, "account/register.html", {"form": form})


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            password1 = form.cleaned_data["password1"]
            if password1 != form.cleaned_data["password2"]:
                form.add_error("password2", "Les mots de passe ne correspondent pas.")
            else:
                Account.objects.create_user(
                    username=form.cleaned_data["username"],
                    email=form.cleaned_data["email"],
                    password=password1,
                )
                messages.success(
                    request, "Inscription réussie. Veuillez vous connecter."
                )
                return redirect("account:login")
    else:
        form = RegisterForm()
    return render(request, "account/register.html", {"form": form})


from .forms import LoginForm, RegisterForm, TOTPForm
from .models import Account


def make_qr_base64(uri):
    # Transform the URI into a QR code image and return it as a base64-encoded string
    image = qrcode.make(uri)  # create a QR code image from the URI in the memory
    buffer = io.BytesIO()  # create a fake file in memory to hold the image
    image.save(buffer, format="PNG")  # write the image to the fake file in PNG format
    return base64.b64encode(
        buffer.getvalue()
    ).decode()  # bytes to base64 string and decode to UTF-8


def generate_backup_codes(user, count=10):
    # Generate backup codes for a user and return them as a list of strings.
    device, _ = StaticDevice.objects.get_or_create(user=user, name="Backup Codes")
    device.token_set.all().delete()  # delete any existing backup codes for the user

    codes = []
    for _ in range(count):
        token = StaticToken.random_token()
        device.token_set.create(token=token)
        codes.append(token)
    return codes


# Create your views here.
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(
                    "account:mfa-verify"
                )  # Redirect to the MFA verification page after successful login
            else:
                form.add_error(None, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = LoginForm()

    return render(request, "account/login.html", {"form": form})


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password1 = form.cleaned_data["password1"]
            password2 = form.cleaned_data["password2"]

            if password1 != password2:
                form.add_error("password2", "Les mots de passe ne correspondent pas.")
            else:
                # Create the user
                user = Account.objects.create_user(
                    username=username, email=email, password=password1
                )
                login(request, user)
                messages.success(
                    request, "Inscription réussie. Veuillez vous connecter."
                )
                return redirect(
                    "account:login",
                )  # Redirect to the login page after successful registration
    else:
        form = RegisterForm()
    return render(request, "account/register.html", {"form": form})


@login_required
def mfa_setup(request):
    if user_has_device(request.user):
        # If the user already has a device, redirect them to the MFA verification page
        return redirect("account:mfa-verify")
    else:
        device, _ = TOTPDevice.objects.get_or_create(
            user=request.user,
            confirmed=False,  # Find or create a TOTP device for the user, but do not confirm it yet
            defaults={"name": "Phone"},
        )
        if request.method == "POST":
            form = TOTPForm(request.POST)
            if form.is_valid():
                if device.verify_token(form.cleaned_data["code"]):
                    device.confirmed = True
                    device.save()
                    django_otp.login(request, device)
                    request.session["backup_codes"] = generate_backup_codes(
                        request.user  # Generate backup codes for the user and store them in the session
                    )
                    return redirect("account:mfa-backup-codes")
                form.add_error("code", "Code incorrect.")
        else:
            form = TOTPForm()
        uri = device.config_url
        return render(
            request,
            "account/mfa_setup.html",
            {
                "qr_code": make_qr_base64(uri),
                "form": form,
            },
        )


@login_required
def mfa_verify(request):
    if not user_has_device(request.user):
        return redirect("account:mfa-setup")

    if request.method == "POST":
        form = TOTPForm(request.POST)
        if form.is_valid():
            device = match_token(
                request.user, form.cleaned_data["code"]
            )  # Try to match the provided totp code by the user with each of the user's devices.
            if device is not None:
                django_otp.login(request, device)
                return redirect("dashboard:home")
            form.add_error("code", "Code incorrect.")
    else:
        form = TOTPForm()

    # Atteint en GET, et en POST quand le code est faux
    return render(request, "account/mfa_verify.html", {"form": form})


@otp_required
def mfa_backup_codes(request):
    codes = request.session.pop("backup_codes", None)
    if (
        codes is None
    ):  # If there are no backup codes in the session, redirect to the dashboard home page
        return redirect("dashboard:home")
    return render(request, "account/mfa_backup_codes.html", {"codes": codes})
