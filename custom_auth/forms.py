from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from user.models import User


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["email", "DOB", "first_name", "last_name", "password1", "password2"]
        widgets = {
                   "DOB":forms.DateInput({"type":"date"})
                }

class LoginForm(AuthenticationForm):
    username = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"placeholder":"Email"}))
    password = forms.CharField(required=True, widget=forms.PasswordInput())


