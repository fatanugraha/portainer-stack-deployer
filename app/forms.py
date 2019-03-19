from django import forms
from django.contrib.auth import authenticate
from django.forms import ValidationError


class LoginForm(forms.Form):
    username = forms.CharField(label="username", max_length=100)
    password = forms.CharField(label="password", max_length=100)

    def clean(self):
        form_data = self.cleaned_data
        username = form_data.get("username")
        password = form_data.get("password")

        if username and password:
            user = authenticate(
                username=form_data["username"], password=form_data["password"]
            )
            if user is None:
                raise ValidationError("Wrong username/password")
            form_data["user"] = user

        return form_data
