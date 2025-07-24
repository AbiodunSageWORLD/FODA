from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import Context
from django.template.loader import get_template
from foda.settings import EMAIL_HOST_USER

import uuid # For generating unique codes
from datetime import timedelta

from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.





def unique_code():
    code = str(uuid.uuid4().hex[:6]).upper() # Or use secrets.token_hex(3)

    while User.objects.filter(verification_code=code).exists():
        code = str(uuid.uuid4().hex[:6]).upper()

    return code


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
    DOB = models.DateField(verbose_name="D.O.B", auto_now=False, auto_now_add=False, null=True)
    email = models.EmailField(verbose_name="Email Address", max_length=254, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=100)
    phone = PhoneNumberField(region="NG", null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False)
    date_joined = models.DateField(default=timezone.now)

    verification_code = models.CharField(max_length=6, blank=True, null=True, unique=True)
    verification_code_expires_at = models.DateTimeField(blank=True, null=True)

    old_cart = models.JSONField(null=True, blank=True)
    
    # Add related_name to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='customuser_set', # Unique related_name
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_permissions_set', # Use another unique related_name
        related_query_name='customuser_permission'
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()
# Define User Types
    USER_TYPE_CHOICES = (
        ("customer", "Customer"),
        ("vendor", "Vendor"),
    )

    

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default="customer")

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.first_name

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.strip().capitalize()
        self.last_name = self.last_name.strip().capitalize()
        self.full_name = f"{self.last_name} {self.first_name}"
        super().save(*args, **kwargs)

    def generate_verification_code(self):
        # Generate a 6-digit alphanumeric code
        self.verification_code = unique_code()
        self.verification_code_expires_at = timezone.now() + timedelta(minutes=10) # Code expires in 10 minutes
        self.save()
        self.send_verification_code()
        
    def send_verification_code(self):
        htmly = get_template("auth/email_verification.html")

        data = {
            "first_name":self.first_name,
            "verification_code": self.verification_code
        }

        html_content = htmly.render(data)

        subject = "Welcome"

        msg =EmailMultiAlternatives(subject=subject, body=html_content, 
                                    from_email=EMAIL_HOST_USER, to=[self.email])
        
        msg.attach_alternative(html_content, "text/html")

        msg.send()

    def is_verification_code_valid(self):
        return self.verification_code and self.verification_code_expires_at and \
               self.verification_code_expires_at > timezone.now()

    def activate(self):
        self.is_active = True
        self.verification_code = None # Clear the code after activation
        self.verification_code_expires_at = None # Clear expiration time
        self.save()
    
    

class Address(models.Model):
    user = models.ForeignKey(User, related_name="address", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=100)
    phone = PhoneNumberField(region="NG", null=True)
    street = models.CharField( max_length=50,)
    city = models.CharField( max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField( max_length=50)

    def __str__(self):
        return f"{self.last_name} {self.first_name} Address"
    
    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"


    def save(self, *args, **kwargs):
        self.first_name = self.first_name.strip().capitalize()
        self.last_name = self.last_name.strip().capitalize()
        self.full_name = f"{self.last_name} {self.first_name}"
        super().save(*args, **kwargs)
    
