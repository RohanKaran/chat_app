from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Fieldset, Layout, Submit
from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class UserRegistrationForm(UserCreationForm):
    helper = FormHelper()

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

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset(
                "Personal Information",
                "first_name",
                "last_name",
                "email",
                "phone",
                "gender",
                "country",
            ),
            Fieldset(
                "User Credentials",
                "password1",
                "password2",
            ),
            Fieldset(
                "Interests",
                "interests",
            ),
        )
        self.helper.add_input(Submit("submit", "Register"))


class LoginForm(forms.Form):
    username = forms.CharField(label="Email/Phone number")
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            HTML(
                '{% if form.errors %}<p class="errornote">Please correct the error below.</p>{% endif %}'
            ),
            "username",
            "password",
        )
        self.helper.add_input(Submit("submit", "Login"))
