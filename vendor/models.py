from django.db import models
from django.conf import settings
from sorl.thumbnail import ImageField

class Vendor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor',null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=100)
    image = ImageField(upload_to='vendors/', blank=True, null=True)

    def __str__(self):
        return self.name
