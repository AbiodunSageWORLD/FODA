from django.db import models
from django.conf import settings
from django.utils.text import slugify
from sorl.thumbnail import ImageField

from datetime import time
from .utils import get_current_day_and_time, get_next_day

class Vendor(models.Model):
    vendor = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor',null=True, blank=True)
    email = models.EmailField(unique=True,null=True, blank=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=255,blank=True, null=True)
    description = models.TextField()
    location = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=100)
    image = ImageField(upload_to='vendors/', blank=True, null=True)
    slug = models.SlugField(unique=True, null=True)

    def __str__(self):
        return self.name
    
    def is_open(self):
        day, time = get_current_day_and_time()

        today_hours = self.business_hour.filter(day=day).first()

        if not today_hours or not today_hours.is_open:
            return False
        
        return today_hours.open_time <= time <= today_hours.close_time
    
    def next_open(self):
        # Loop through a range of 7 till we get the next business hour
        for i in range(7):
            """
            Get the next open day
            if i == 0, next open day is today
            if i == 1, next day is tommorow
            """
            day, time = get_next_day(number=i)

            # Filters through the related business hour linked to Vendor 
            # checking the day and if it is opened for that day
            hours = self.business_hour.filter(day=day, is_open=True).first()

            if hours:
                if i == 0 and time < hours.open_time:
                    return f"OPENS TODAY AT {hours.open_time.strftime('%I:%M %p')}".upper()
                
                elif i == 1:
                    return f"OPENS TOMMOROW AT {hours.open_time.strftime('%I:%M %p')}".upper()
                
                elif i > 1:
                    return f"OPENS ON {BusinessHour.Days(hours.day).label} AT {hours.open_time.strftime('%I:%M %p')}".upper()

        return  f"BUSINESS IS CLOSED"
                    
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class BusinessHour(models.Model):
    class Days(models.TextChoices):
        SUNDAY = "SUN", "Sunday"
        MONDAY = "MON", "Monday" 
        TUESDAY = "TUE", "Tuesday"
        WEDNESDAY = "WED", "Wednesday"
        THURSDAY = "THU", "Thursday"
        FRIDAY = "FRI", "Friday"
        SATURDAY = "SAT", "Saturday"

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="business_hour")
    day = models.CharField(max_length=50, choices=Days)
    open_time = models.TimeField(default=time(9, 0, 0), auto_now=False, auto_now_add=False)
    close_time = models.TimeField(default=time(16, 0, 0), auto_now=False, auto_now_add=False)
    is_open = models.BooleanField(default=False)

    class Meta:
        unique_together = ("vendor", "day")
        verbose_name = "Vendor Business Hour"
        verbose_name_plural = "Vendor Business Hours"
        ordering = ["vendor", "id"]

    def __str__(self):
        return f"{self.vendor.name} - {self.get_day_display()}"
    