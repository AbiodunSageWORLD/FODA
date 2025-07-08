from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from phonenumber_field.widgets import PhoneNumberPrefixWidget
from phonenumber_field.formfields import SplitPhoneNumberField

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
        fields = ["email", "DOB", "first_name", "last_name", "phone"]
        widgets = {"email":forms.EmailInput({"readonly":True}),
                   "DOB":forms.DateInput({"type":"date"})
                }

class Addressform(forms.ModelForm):
    class Meta:
        model = Address
        exclude =["user", "full_name"]
        # widgets = {"phone":PhoneNumberPrefixWidget()}