from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label="Your Username", max_length=50)
    password = forms.CharField(label="Your Password", widget=forms.PasswordInput)
