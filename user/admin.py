from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Address

from .forms import CustomUserCreationForm, CustomUserChangeForm

# Register your models here.

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ("email", "full_name", "is_superuser", "is_vendor", "is_staff")
    list_filter = ("is_superuser", "is_vendor", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Details",{"fields":("first_name", "last_name", "full_name", "phone", "DOB")}),
        ("Permissions", {"fields": ("is_vendor", "is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Address)
