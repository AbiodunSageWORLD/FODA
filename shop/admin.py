from django.contrib import admin
from .models import Food, Customer, OrderItem, Order

# Register your models here.
admin.site.register(Food)
admin.site.register(Customer)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ["food"]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "order_date", "paid"]
    search_fields = ["id",]
    list_filter = ["order_date", "paid"]
    inlines = [OrderItemInline]
