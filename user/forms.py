from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User, Address

# strictly used for the admin
class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("email",)

# strictly used for the admin
class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ("email",)


class EditUserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ["email", "DOB", "first_name", "last_name"]

class Addressform(forms.ModelForm):

    class Meta:
        model = Address
        exclude =["user", "full_name"]