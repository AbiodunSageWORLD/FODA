from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import uuid # For generating unique codes
from datetime import timedelta

# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):

        if not email:
            raise ValueError(_("The email must be set"))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Super User must have is_staff=True"))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Super User must have is_superuser=True"))
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    DOB = models.DateField(verbose_name="D.O.B", auto_now=False, auto_now_add=False)
    email = models.EmailField(verbose_name="Email Adress", max_length=254, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateField(default=timezone.now)

    verification_code = models.CharField(max_length=6, blank=True, null=True, unique=True)
    verification_code_expires_at = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["DOB", "first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.first_name

    def save(self, *args, **kwargs):
        self.full_name = f"{self.last_name} {self.first_name}"
        super().save(*args, **kwargs)

    def generate_verification_code(self):
        # Generate a 6-digit alphanumeric code
        self.verification_code = unique_code()
        self.verification_code_expires_at = timezone.now() + timedelta(minutes=10) # Code expires in 10 minutes
        self.save()

    def is_verification_code_valid(self):
        return self.verification_code and self.verification_code_expires_at and \
               self.verification_code_expires_at > timezone.now()

    def activate(self):
        self.is_active = True
        self.verification_code = None # Clear the code after activation
        self.verification_code_expires_at = None # Clear expiration time
        self.save()


def unique_code():
    code = str(uuid.uuid4().hex[:6]).upper() # Or use secrets.token_hex(3)

    while User.objects.filter(verification_code=code).exists():
        code = str(uuid.uuid4().hex[:6]).upper()

    return code