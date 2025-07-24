from django.db import models
from vendor.models import Vendor
from sorl.thumbnail import ImageField

from phonenumber_field.modelfields import PhoneNumberField
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
    def __str__(self):
        return f"{self.name} - {self.vendor.name}"

class Customer(models.Model):
    user = models.OneToOneField('user.User', on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Status(models.TextChoices):
        PENDING = "PD", "Pending"
        CONFIRMED = "CF", "Confirmed"
        SENT = "ST", "Sent"
        DELIVERED = "DL", "Delivered" 
        CANCELLED = "CN", "Cancelled"


# Assign a numeric value to each status for easy comparison
# This mapping needs to be consistent with the desired hierarchy
STATUS_ORDER = {
    Status.PENDING: 1,
    Status.CONFIRMED: 2,
    Status.SENT: 3,
    Status.DELIVERED: 4,
    Status.CANCELLED: 0, # Canceled items should likely not advance order status
}

    
class Order(models.Model):

    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    phone = PhoneNumberField(region="NG", null=True)
    street = models.CharField( max_length=50, null=True,)
    city = models.CharField( max_length=50, null=True)
    state = models.CharField(max_length=50, null=True)
    country = models.CharField( max_length=50, null=True)

    user = models.ForeignKey('user.User', related_name='order', on_delete=models.CASCADE, null=True)
    # quantity = models.PositiveIntegerField(default=1)
    # total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    status = models.CharField(max_length=2, choices=Status, default=Status.PENDING)

    class Meta:
        ordering = ["-order_date"]
    
    def __str__(self):
        return f"Order #{self.id} - {self.get_full_name()} - {self.status}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_total_price(self):
        return sum(item.get_item_total for item in self.order_item.all())
    
    def get_total_quantity(self):
        return sum(item.quantity for item in self.order_item.all())

     # --- Core Logic for Status Update ---
    def update_overall_status(self):
        """
        Calculates and updates the overall order status based on its order items.
        The order status will be the "lowest" status among all its items,
        unless all items have reached a final status like DELIVERED.
        """
        order_items = self.order_item.all()
        if not order_items:
            # If no items, status remains pending or can be set to cancelled, etc.
            # Define your desired behavior for empty orders.
            if self.status != Status.PENDING:
                self.status = Status.PENDING # Or Status.CANCELLED
                self.save(update_fields=['status'])
            return

        # Get all item statuses and their corresponding "order" values
        item_statuses_values = [STATUS_ORDER.get(item.status, 0) for item in order_items]

        # Determine the "lowest" (least advanced) status among items
        min_status_value = min(item_statuses_values)

        # Check if all items are delivered
        all_delivered = all(item.status == Status.DELIVERED for item in order_items)
        # Check if all items are cancelled
        all_cancelled = all(item.status == Status.CANCELLED for item in order_items)


        new_status = self.status # Start with current status

        if all_delivered:
            new_status = Status.DELIVERED
        elif all_cancelled:
            new_status = Status.CANCELLED
        else:
            # Find the status corresponding to the min_status_value
            # This handles cases where some items are more advanced than others
            # The order status should reflect the least advanced non-cancelled item
            if Status.PENDING in [item.status for item in order_items]:
                new_status = Status.PENDING
            elif Status.CONFIRMED in [item.status for item in order_items]:
                new_status = Status.CONFIRMED
            elif Status.SENT in [item.status for item in order_items]:
                new_status = Status.SENT
            # You might need more complex logic here depending on partial deliveries
            # E.g., if some delivered, some sent -> Status.SENT (partially delivered)

            # More robust way to derive status from min_status_value (excluding cancelled)
            active_item_statuses = [item.status for item in order_items if item.status != 
            Status.CANCELLED]
            if active_item_statuses:
                # Find the minimum status value among active items
                min_active_status_value = min(STATUS_ORDER.get(s, 0) for s in active_item_statuses)
                # Find the status string that matches this min value
                for status_code, status_name in Status.choices:
                    if STATUS_ORDER.get(status_code) == min_active_status_value:
                        new_status = status_code
                        break
            else: # All items are cancelled
                new_status = Status.CANCELLED

        if new_status != self.status:
            self.status = new_status
            self.save(update_fields=['status']) # Only save the 'status' field



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_item")
    food = models.ForeignKey(Food, related_name='orders', on_delete=models.CASCADE)
    vendor = models.ForeignKey("vendor.Vendor", related_name='orders', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=2, choices=Status, default=Status.PENDING)
    
    def __str__(self):
        return f"Order of {self.food.name} - Quantity: {self.quantity}"
    
    def get_item_total(self):
        return float(self.quantity) * float(self.price)


    def save(self, *args, **kwargs):
        self.vendor = self.food.vendor
        super().save(*args, **kwargs) # Save the OrderItem first

        # After saving the item, update the overall order status
        # This will trigger the `update_overall_status` method on the related Order
        
        self.order.update_overall_status()
