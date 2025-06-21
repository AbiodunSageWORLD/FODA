from django.db import models
from vendor.models import Vendor
from sorl.thumbnail import ImageField

# Create your models here.
    
class Food(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_sale = models.BooleanField(default=False)
    vendor = models.ForeignKey(Vendor, related_name='foods', on_delete=models.CASCADE)
    image = ImageField(upload_to='foods/', blank=True, null=True)
    
    def __str__(self):
        return self.name

class Customer(models.Model):
    user = models.OneToOneField('user.User', on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Order(models.Model):
    food = models.ForeignKey(Food, related_name='orders', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order of {self.food.name} - Quantity: {self.quantity}"