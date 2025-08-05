from django.db import models
from django.conf import settings
from sorl.thumbnail import ImageField
from .utils import get_current_day_and_time

class Vendor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor',null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=100)
    image = ImageField(upload_to='vendors/', blank=True, null=True)

    def __str__(self):
        return self.name
    
    def is_open(self):
        day, time = get_current_day_and_time()

        today_hours = self.business_hour.filter(day=day)[0]

        if not today_hours or not today_hours.is_open:
            return False
        
        return today_hours.open_time <= time <= today_hours.close_time


class BusinessHour(models.Model):
    class Days(models.TextChoices):
        SUNDAY = "SUN", "Sunday"
        MONDAY = "MON", "Monday" 
        TUESDAY = "TUE", "Tuesday"
        WEDNESDAY = "WED", "Wednesday"
        THURSDAY = "THU" "Thursday"
        FRIDAY = "FRI", "Friday"
        SATURDAY = "SAT", "Saturday"

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="business_hour")
    day = models.CharField(max_length=50, choices=Days)
    open_time = models.TimeField(auto_now=False, auto_now_add=False)
    close_time = models.TimeField(auto_now=False, auto_now_add=False)
    is_open = models.BooleanField(default=False)

    class Meta:
        unique_together = ("vendor", "day")
        verbose_name = "Vendor Business Hour"
        verbose_name_plural = "Vendor Business Hours"
        ordering = ["vendor", "day"]

    def __str__(self):
        return f"{self.vendor.name} - {self.vendor.get_day_display()}"
    