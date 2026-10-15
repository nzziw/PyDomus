from django import forms

from .models import Account


class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=50)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    username = forms.CharField(label="Username", max_length=50)
    email = forms.EmailField(label="Email")
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Confirmer le mot de passe", widget=forms.PasswordInput
    )

    # Custom validation to ensure that the username is unique
    def clean_username(self):
        username = self.cleaned_data["username"]
        if Account.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà utilisé.")
        return username

    # Custom validation to ensure that the email is unique
    def clean_email(self):
        email = self.cleaned_data["email"]
        if Account.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Cette adresse e-mail est déjà utilisée.")
        return email

    def clean(self):
        cleaned_data = (
            super().clean()
        )  # Call the parent class's clean method to get the cleaned data
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")


class TOTPForm(forms.Form):
    code = forms.CharField(label="Code", max_length=8)
