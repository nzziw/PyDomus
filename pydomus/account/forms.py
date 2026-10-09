from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label="Your Username", max_length=50)
    password = forms.CharField(label="Your Password", widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    username = forms.CharField(label="Your Username", max_length=50)
    email = forms.EmailField(label="Your Email")
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = (
            super().clean()
        )  # Call the parent class's clean method to get the cleaned data
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
