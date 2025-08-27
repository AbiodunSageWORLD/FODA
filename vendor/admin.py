from django.contrib import admin
from .models import Vendor, BusinessHour

# Register your models here.
class BusinessHourAdmin(admin.TabularInline):
    model = BusinessHour
    extra = 0
    max_num = 7

class VendorAdmin(admin.ModelAdmin):
    inlines =[BusinessHourAdmin]

admin.site.register(Vendor, VendorAdmin)
