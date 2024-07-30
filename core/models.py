from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurants')

    def __str__(self):
        return self.name

class Floor(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='floors')
    name = models.CharField(max_length=50)  

    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"

class Table(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
    ]
    number = models.IntegerField()
    capacity = models.IntegerField()
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='tables')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"Table {self.number} ({self.floor})"
    
    def close_table(self):
        self.status = 'available'
        self.save()
        for order in self.orders.filter(status__in=['pending', 'preparing', 'ready', 'delivered']):
            order.complete()


class Category(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"

    class Meta:
        unique_together = ('restaurant', 'name')

class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.category.restaurant.name} - {self.name}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('delivered', 'Delivered'),
        ('paid', 'Paid'),
        ('completed', 'Completed'),
    ]
    table = models.ForeignKey('Table', on_delete=models.SET_NULL, null=True, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.table.floor.restaurant.name} - Order {self.id} - Table {self.table.number}"

    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())

    def complete(self):
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def get_subtotal(self):
        return self.quantity * self.menu_item.price

    def __str__(self):
        return f"{self.order} - {self.menu_item.name}"