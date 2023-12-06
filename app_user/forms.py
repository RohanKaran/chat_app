from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "gender",
            "country",
            "password1",
            "password2",
            "interests",
        ]


class LoginForm(forms.Form):
    username = forms.CharField(label="Email/Phone number")
    password = forms.CharField(widget=forms.PasswordInput)
