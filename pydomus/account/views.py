from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm
from .models import Account


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
                return redirect("/")
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
                return redirect(
                    "account:login"
                )  # Redirect to the login page after successful registration
    else:
        form = RegisterForm()
    return render(request, "account/register.html", {"form": form})
